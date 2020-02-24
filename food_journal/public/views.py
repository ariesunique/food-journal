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
from flask_login import login_required, login_user, logout_user, current_user

from food_journal.extensions import login_manager
from food_journal.public.forms import LoginForm, FoodForm
from food_journal.user.forms import RegisterForm
from food_journal.user.models import User
from food_journal.public.models import FoodItem
from food_journal.utils import flash_errors
from food_journal.database import db

from werkzeug.utils import secure_filename

from datetime import datetime


blueprint = Blueprint("public", __name__, static_folder="../static")



@blueprint.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))

    
@blueprint.route("/")
@blueprint.route("/index")
def index():
    form = LoginForm()

    if current_user and current_user.is_authenticated:
        foodList = current_user.food_items.order_by(FoodItem.created_at.desc()).all()
    else:
        # arbitrarily limiting num results to 20 -- FIX ME
        foodList = FoodItem.query.filter_by(is_public=True).order_by(FoodItem.created_at.desc()).all()    

    return render_template("public/index.html", form=form, foodList=foodList)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.index"))


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
        return redirect(url_for("public.index"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/add/", methods=["GET", "POST"])
def add_dish():
    """Add a new image"""    
    form = FoodForm()
    
    if form.validate_on_submit():

        fooditem = FoodItem.create(
            title=form.title.data,
            comment=form.comment.data,
            image = form.image.data,
            author= current_user,
            is_public = form.is_public.data
        )                       
        if fooditem.persistent:
            flash("Thank you for adding a dish.", "success")
        else:
            flash("Sorry, there was an error uploading your image. Please try again later.", "danger")
        return redirect(url_for("public.index"))
    else:
        flash_errors(form)
    return render_template("public/add-dish.html", form=form)




@blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Home page."""
    form = LoginForm()

    # Handle logging in 
    if form.validate_on_submit():
        login_user(form.user)
        flash("You are logged in.", "success")
        redirect_url = request.args.get("next") or url_for("public.index")
        return redirect(redirect_url)
    else:
        flash_errors(form)
    return redirect(url_for('public.index'))


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)


