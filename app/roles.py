from flask_roles import RoleManager
import flask_login
from flask import render_template


def unauthorized_callback():
    return render_template('unauthorized.html')


role_manager = RoleManager(
    role_loader=lambda: flask_login.current_user,
    default_unauthorized_callback=unauthorized_callback,
    other_decorator=flask_login.login_required
)
