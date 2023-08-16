from .db import db
from flask import render_template, request, Blueprint, session
from .models import Docente
from .models import Persona
from .login import login_manager
import flask_login

view = Blueprint('view', __name__)


@view.route('/')
def index():
    session['cod_docente'] = 'P01'
    results = db.session.execute(db.select(Docente).where(Docente.cod_docente == 'P01')).first()

    for result in results:
        docente = result

    return render_template('dashboard.html', docente=docente)


@view.route('/users')
def get_users():
    users = db.session.execute(db.select(Persona)).scalars()
    return render_template('users.html', users=users)


@view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

