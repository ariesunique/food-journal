# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from food_journal.user.models import User
from food_journal.user.forms import EditProfileForm


blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")




@blueprint.route("/")
@login_required
def members():
    """List members."""
    return render_template("users/members.html")


@blueprint.route("/<username>")
@login_required
def profile(username):
    """Return user's profile page"""
    print("here")
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("users/profile.html", user=user)


@blueprint.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.update(about_me=form.about_me.data)
        flash("Your changes have been saved.")
        return redirect(url_for('user.edit_profile'))
    elif request.method == 'GET':        
        form.about_me.data = current_user.about_me
    return render_template('users/edit_profile.html', title='Edit Profile', form=form)
        

@blueprint.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    current_user.save()
    flash('You are now following {}!'.format(username))
    return redirect(url_for('user.profile', username=username))

@blueprint.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('public.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user.profile', username=username))
    current_user.unfollow(user)
    current_user.save()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user.profile', username=username))

        