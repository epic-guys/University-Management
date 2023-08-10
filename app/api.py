from flask import Blueprint
from .models import Utente
from .db import db

api = Blueprint('api', __name__)

users = [
    {
        'first_name': 'paolo',
        'last_name': 'brosio'
    },
    {
        'first_name': 'dio',
        'last_name': 'mio'
    }
]


@api.route('/user/<user_id>')
def get_user(user_id):
    stmt = db.select(Utente).where(Utente.id_utente == user_id)
    u: Utente = db.session.execute(stmt).scalars().first()
    return u.to_json()
