from flask import render_template, request, Blueprint, session, url_for, flash, redirect, abort
import argon2
from ..models import *
import flask_login
from ..roles import view_role_manager
from .studenti import studenti
from .docenti import docenti

password_hasher = argon2.PasswordHasher()

view = Blueprint('view', __name__)


view.register_blueprint(studenti)
view.register_blueprint(docenti)


@flask_login.login_required
@view.route('/')
def index():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('view.login'))
    if isinstance(flask_login.current_user, Docente):
        return redirect(url_for('view.docenti.index'))
    else:
        return redirect(url_for('view.studenti.index'))


@view.route('/users')
def get_users():
    users = db.session.execute(db.select(Persona)).scalars()
    return render_template('users.html', users=users)


@view.route('/login', methods=['GET', 'POST'])
def login():
    if not flask_login.current_user.is_authenticated:
        if request.method == 'GET':
            return render_template('login.html')

        email = request.form['email']
        password = request.form['password']
        query = select(Persona).where(Persona.email == email)
        user = db.session.scalar(query)
        try:
            password_hasher.verify(user.password_hash, password)
            flask_login.login_user(user)
        except (argon2.exceptions.VerifyMismatchError, AttributeError) as e:
            flash("Credenziali errate", 'error')
            return render_template('login.html')

    return redirect(url_for('view.index'))


@view.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('view.index'))

