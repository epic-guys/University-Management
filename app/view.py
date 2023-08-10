from .db import db
from flask import render_template, request, Blueprint
from .models import Utente

view = Blueprint('view', __name__)


@view.route('/')
def index():
    return render_template('dashboard.html')


@view.route('/users')
def get_users():
    users = db.session.execute(db.select(Utente)).scalars()
    return render_template('users.html', users=users)


@view.route('/login', methods=['GET, POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
