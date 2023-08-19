from flask import Blueprint, request
from .models import Persona, Esame
from .db import db
from sqlalchemy import select

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


@api.route('/esame', method='POST')
def insert_esame():
    esame = Esame.from_json(request.json['esame'])

    pass
