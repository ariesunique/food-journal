# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    Response,
)
from flask_login import login_required, login_user, logout_user

from food_journal.extensions import login_manager
from food_journal.public.forms import LoginForm, FoodForm
from food_journal.user.forms import RegisterForm
from food_journal.user.models import User
from food_journal.public.models import FoodItem
from food_journal.utils import flash_errors

from werkzeug.utils import secure_filename

import os
import boto3
import requests
import random

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))

    
@blueprint.route("/")
@blueprint.route("/index")
def index():
    form = LoginForm(request.form)
    # arbitrarily limiting num results to 20 
    foodList = FoodItem.query.all()

    return render_template("public/index.html", form=form, foodList=foodList)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/add/", methods=["GET", "POST"])
def add_dish():
    """Add a new image"""
    #current_app.logger.info("bucket from config is: {}".format( current_app.config["BUCKET_NAME"]) )
    BUCKET = current_app.config["S3_BUCKET_NAME"]
    form = FoodForm(request.form)
    
    
    if form.validate_on_submit():
        
        current_app.logger.info("User is attempting to add a dish.")
        
        current_app.logger.info(form)      
        
        if request.files:
            image = request.files["image"]     
            current_app.logger.info(image)
            
            filename = secure_filename(image.filename)
            full_filename = os.path.join(current_app.instance_path, filename)
            current_app.logger.info("Filename: {}".format( full_filename))
            
            image.save(full_filename)
            aws_image_object_name =  "{}-{}".format( random.randint(1111,9999), filename)
            upload_file(full_filename, BUCKET, aws_image_object_name )

        fooditem = FoodItem.create(
            title=form.title.data,
            comment=form.comment.data,
            aws_key=aws_image_object_name
        )              
            
        #fooditem.aws_image_object_name = aws_image_object_name
        #fooditem.update()
        
        #filename = secure_filename(form.image.data.filename)
        #full_filename = os.path.join(app.instance_path, 'photos', filename)
        #f.save(full_filename)
        #upload_file(full_filename, BUCKET)
        

        flash("Thank you for adding a dish.", "success")
        return redirect(url_for("public.index"))
    else:
        flash_errors(form)
    return render_template("public/add-dish.html", form=form)


def upload_file(full_path, bucket, filename):
    """
    TODO - this should probably be moved
    Function to upload a file to an S3 bucket
    """
    #object_name = filename
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(full_path, bucket, filename)
    #current_app.logger.info("AWS response", response)

    return response

# -----------------------
#Old stuff that I don't need anymore
@blueprint.route("/old", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)


