from flask_roles import RoleManager
import flask_login
from flask import render_template, jsonify


def view_unauthorized_callback():
    return render_template('unauthorized.html'), 403


def api_unauthorized_callback():
    return jsonify({'status': 'fail', 'data': {'message': 'User is not authorized'}}), 403


def role_loader():
    return flask_login.current_user


view_role_manager = RoleManager(
    role_loader=role_loader,
    default_unauthorized_callback=view_unauthorized_callback,
    other_decorator=flask_login.login_required
)

api_role_manager = RoleManager(
    role_loader=role_loader,
    default_unauthorized_callback=api_unauthorized_callback,
    other_decorator=flask_login.login_required
)
