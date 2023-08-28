from .db import db
from sqlalchemy import select
from flask import render_template, request, Blueprint, session, url_for, flash, redirect
from .models import Docente, Studente
from .models import Persona
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
    return '<h1>Studente</h1>'


@docenti.route('/')
def index():
    query = select(Docente).where(Docente.cod_docente == '01')
    docente = db.session.scalar(query)
    return render_template('dashboard.html', docente=docente)


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


@view.route('/calendar')
def calendar():
    return render_template('calendar.html')


@view.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('view.index'))