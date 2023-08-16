from .db import db
from flask import render_template, request, Blueprint, session
from .models import Persona
from .login import login_manager
import flask_login

view = Blueprint('view', __name__)


@view.route('/')
def index():
    session['cod_persona'] = 'P01'
    persona = db.session.execute(db.select(Persona).where(Persona.cod_persona == 'P01')).first()
    return render_template('dashboard.html', persona=persona)


@view.route('/users')
def get_users():
    users = db.session.execute(db.select(Persona)).scalars()
    return render_template('users.html', users=users)


@view.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'GET':
        return render_template('login.html')

