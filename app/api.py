import json

from flask import Blueprint, request
from .models import Persona, Esame
from .db import db
from sqlalchemy import select, update, delete, insert

api = Blueprint('api', __name__)


def insert_esame():
    # TODO opportuna sanificazione dell'input
    db.session.execute(insert(Esame), request.json['esame'])

def delete_esame(cod):
    """
    TODO pure qua sanificare, sarebbe ancora più bello magari far sì che gli
    esami non si elimino dal database ma si "annullano", in modo da gestire
    un ipotetico annullamento dell'esame.
    """
    db.session.execute(delete(Esame).where(Esame.cod_esame == cod))


@api.route('/esami')
def tutti_esami():
    esami = db.session.scalars(select(Esame)).all()
    esami_json = [e.to_json() for e in esami]
    return esami_json


@api.route('/esami/<cod>')
def esami(cod):
    match request.method:
        case 'GET':
            return 69
        case 'POST':
            return insert_esame()
        case 'DELETE':
            return delete_esame(cod)
