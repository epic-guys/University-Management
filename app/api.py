import json

from flask import Blueprint, request
from .models import Persona, Esame, Appello, Prova, Model
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


def jsonify_list(l: list[Model]):
    return json.dumps([elem.to_json() for elem in l])


@api.route('/esami/', methods=['GET', 'DELETE'])
@api.route('/esami/<cod_esame>', methods=['GET', 'DELETE'])
def esami(cod_esame=None):
    match request.method:
        case 'GET':
            query = select(Esame)
            if cod_esame is not None:
                query = query.where(Esame.cod_esame == cod_esame)
            esami = db.session.scalars(query).all()
            return jsonify_list(esami)
        case 'POST':
            return insert_esame()
        case 'DELETE':
            return delete_esame(cod_esame)


@api.route('/prove/<cod_esame>')
@api.route('/prove/<cod_esame>/<cod_prova>')
def prove(cod_esame, cod_prova=None):
    match request.method:
        case 'GET':
            query = select(Prova).where(Prova.cod_esame == cod_esame)
            if cod_prova is not None:
                query = query.where(Prova.cod_prova == cod_prova)
            prove = db.session.scalars(query).all()
            return jsonify_list(prove)


@api.route('/docenti/<cod_docente>/prove')
def prove_docenti(cod_docente):
    prove = db.session.scalars(select(Prova).where(Prova.cod_docente == cod_docente)).all()
    return jsonify_list(prove)
