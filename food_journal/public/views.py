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
)
from flask_login import login_required, login_user, logout_user

from food_journal.extensions import login_manager
from food_journal.public.forms import LoginForm, FoodForm
from food_journal.user.forms import RegisterForm
from food_journal.user.models import User
from food_journal.public.models import FoodItem
from food_journal.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", defaults={"id": 3})
@blueprint.route("/index", defaults={"id": 3})
@blueprint.route("/index/<int:id>")
def index(id):
    form = LoginForm(request.form)
    # arbitrarily limiting num results to 20 
    foodList = FoodItem.query.all()
    current_app.logger.info("Id is {}.".format(id))
    return render_template("public/index.html", form=form, foodList=foodList, id=id)


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
    form = FoodForm(request.form)
    current_app.logger.info("User is attempting to add a dish.")
    if form.validate_on_submit():
        fooditem = FoodItem.create(
            title=form.title.data,
            comment=form.comment.data
        )
        flash("Thank you for adding a dish.", "success")
        return redirect(url_for("public.index", id=fooditem.id))
    else:
        flash_errors(form)
    return render_template("public/add-dish.html", form=form)



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


