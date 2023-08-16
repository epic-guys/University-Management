from .db import db
from flask import render_template, request, Blueprint, session
from .models import Docente

view = Blueprint('view', __name__)


@view.route('/')
def index():
    session['cod_docente'] = 'P01'
    docente = db.session.execute(db.select(Docente).where(Docente.cod_docente == 'P01')).first()
    return render_template('dashboard.html', persona=docente)


@view.route('/users')
def get_users():
    users = db.session.execute(db.select(Utente)).scalars()
    return render_template('users.html', users=users)


@view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

