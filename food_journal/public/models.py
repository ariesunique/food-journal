"""Food models"""
import datetime as dt

from flask_login import UserMixin

from food_journal.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)

class FoodItem(SurrogatePK, Model):
    """Store an actual dish the user uploads"""
    __tablename__ = "food"
    title = Column(db.String(80), nullable=False)
    #image = ""
    comment = Column(db.String(200))
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    created_by = Column(db.String(80), nullable=False, default="Anonymous user {}".format(dt.datetime.utcnow()))
    
    def __init__(self, title, **kwargs):
        """Create instance."""
        db.Model.__init__(self, title=title, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<FoodItem({self.title})>"  