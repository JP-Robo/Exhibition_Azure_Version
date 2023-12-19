from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import UserMixin, login_user, logout_user
import os

class User(UserMixin):
    # TODO: what is this for?
    id = "an id"


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    """checks wheather the provided credentials are the same as
    the ones stored in the enviroment variables
    if so a login user is created and the logged in user can view
    the index page

    Returns:
        BaseResponse: redirection to the index page on success
        BaseResponse: redirection to the login page on failure
    """
    username = request.form.get('username')
    password = request.form.get('password')

    env_var_username = os.environ['username']
    env_var_password = os.environ['password']

    if (username == env_var_username):
        if (password == env_var_password):
            user = User()
            user.id = "Schnuser"
            login_user(user)
            return redirect(url_for('index'))
        
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    """when the logout route is called, the user gets redirected to the
    login route

    Returns:
        BaseResponse: "it’s a regular WSGI application", sends the user to the login page
    """
    logout_user()
    return redirect(url_for('auth.login'))


