from .db import db
from sqlalchemy import select
from flask import render_template, request, Blueprint, session, url_for, flash, redirect, abort
from .models import *
import flask_login
from .roles import role_manager

view = Blueprint('view', __name__)
studenti = Blueprint('studenti', __name__, url_prefix='/studenti')
docenti = Blueprint('docenti', __name__, url_prefix='/docenti')


@studenti.before_request
def before_request():
    if not isinstance(flask_login.current_user, Studente):
        return role_manager.default_unauthorized_callback()


@docenti.before_request
def before_request():
    if not isinstance(flask_login.current_user, Docente):
        return role_manager.default_unauthorized_callback()


view.register_blueprint(studenti)
view.register_blueprint(docenti)


@studenti.route('/')
def index():
    return render_template('studenti/dashboard.html')


@docenti.route('/')
def index():
    return render_template('docenti/dashboard.html')


@docenti.route('/esami/')
@docenti.route('/esami/<cod_esame>')
def esami(cod_esame=None):
    if cod_esame is None:
        return render_template('docenti/esami.html')

    q = select(Esame).where(Esame.cod_esame == cod_esame)
    esame = db.session.scalar(q)
    if esame is None:
        return abort(404)

    return render_template('docenti/esame.html', esame=esame)


@docenti.route('/voti/')
def voti():
    return render_template('docenti/voti.html')


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
        # TODO CAMBIARE ASSOLUTAMENTE IN PASSWORD HASH, TEST
        query = select(Persona).where(Persona.email == email and Persona.password_hash == password)
        user = db.session.scalar(query)
        if user is not None:
            flask_login.login_user(user)
        else:
            flash("No user found")
            return render_template('login.html')

    return redirect(url_for('view.index'))


@view.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('view.index'))


@view.route('/appelli')
def appelli():
    return render_template('appelli.html')
