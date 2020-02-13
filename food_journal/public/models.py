"""Food models"""
import datetime as dt
from werkzeug.utils import secure_filename

import os
import boto3
import requests
import random
import tempfile

from botocore.exceptions import ClientError, ParamValidationError

from flask import current_app

from flask_login import UserMixin

from food_journal.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)

class AWS_Mixin(object):
    @classmethod
    def upload_to_s3(cls, model):
        current_app.logger.info("SENDINGTO S3")
        BUCKET = current_app.config["S3_BUCKET_NAME"]
        for field in model.__sendtos3__:
            obj = getattr(model, field)
            filename = secure_filename(obj.filename)
            with tempfile.TemporaryDirectory() as tmpdirname:
                full_filename = os.path.join(tmpdirname, filename)
                #current_app.logger.info("Filename: {}".format( full_filename))
                obj.save(full_filename)
                aws_image_object_name =  "{}-{}".format( random.randint(1111,9999), filename)
                model.aws_key = aws_image_object_name

                s3_client = boto3.client('s3')
                try:
                    response = s3_client.upload_file(full_filename, BUCKET, aws_image_object_name, ExtraArgs={'ACL': 'public-read'})
                except ParamValidationError as e:
                    current_app.logger.error("ParamValidationError caught!!", e)
                    return False
                except ClientError as e:
                    current_app.logger.error("ClientError caught!!", e)
                    return False
        return True
    
    
    @classmethod
    def before_commit(cls, session):
        """
        Before we commit, attempt to save the image to the S3 bucket.
        If the upload is unsuccessful, remove the item from the session.
        This should prevent orphaned images on S3.
        """
        #current_app.logger.info("BEFORE COMMIT")
        for model in list(session.new):
            if isinstance(model, AWS_Mixin):
                sent_to_s3 = AWS_Mixin.upload_to_s3(model)
                if not sent_to_s3:
                    #current_app.logger.info("SEND TO S3 FAILED - REMOVING OBJ FROM SESSION")
                    session.expunge(model)
                    # setting this field to signal to the UI (view) that we did not save this obj
                    model.persistent = False
                else:
                    # setting this field to true since the view will be looking for it (see the note above)
                    model.persistent = True



class FoodItem(SurrogatePK, Model, AWS_Mixin):
    """Store an actual dish the user uploads"""
    
    # list of fields containing data that should be uploaded to s3
    __sendtos3__ = ['image']
    
    __tablename__ = "food"
    title = Column(db.String(80), nullable=False)
    aws_key = Column(db.String(100), nullable=False, unique=True)
    comment = Column(db.String(200))
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    created_by = Column(db.String(80), nullable=False, default="Anonymous user {}".format(dt.datetime.utcnow()))
    
    @property
    def aws_url(self):
        # file should be formatted as follows: https://{bucket_name}.s3.amazonaws.com/{self.aws_key}"
        return current_app.config["S3_OBJECT_URL_TEMPLATE"].format(current_app.config["S3_BUCKET_NAME"], self.aws_key) 

    
    def __init__(self, title, image=None, **kwargs):
        """Create instance."""
        self.image = image 
        db.Model.__init__(self, title=title, **kwargs)
        

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<FoodItem({self.title})>"  
    
    
db.event.listen(db.session, 'before_commit', AWS_Mixin.before_commit)