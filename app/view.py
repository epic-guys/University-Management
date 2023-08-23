from .db import db
from sqlalchemy import select
from flask import render_template, request, Blueprint, session, url_for, flash, redirect
from .models import Docente
from .models import Persona
import flask_login

view = Blueprint('view', __name__)


@flask_login.login_required
@view.route('/')
def index():
    query = select(Docente).where(Docente.cod_docente == '01')
    docente = db.session.scalar(query)
    return render_template('dashboard.html', docente=docente)


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

