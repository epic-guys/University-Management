import json

from flask import Blueprint, request, jsonify, abort
from .models import *
from .db import db
from sqlalchemy import select, update, delete, insert

api = Blueprint('api', __name__)


def insert_esame():
    # TODO opportuna sanificazione dell'input
    db.session.execute(insert(Esame), request.form.to_dict())
    db.session.commit()
    return '', 204


def delete_esame(cod):
    """
    TODO pure qua sanificare, sarebbe ancora più bello magari far sì che gli
    esami non si elimino dal database ma si "annullano", in modo da gestire
    un ipotetico annullamento dell'esame.
    """
    db.session.execute(delete(Esame).where(Esame.cod_esame == cod))


def insert_eventi():
    req = request.form.to_dict()
    req['data_appello'] = req['data'] + 'T' + req['ora']
    req.pop('data', 'ora')
    db.session.execute(insert(Appello), req)
    db.session.commit()
    return "", 204


# TODO Sistemare la relazione nel moddels.py
def insert_iscrizione_appelli():
    db.session.execute(insert(IscrizioneAppello), request.form.to_dict())
    db.session.commit()
    return "", 204


def jsonify_list(l: list[Model], includes=None):
    return jsonify([elem.to_dict(includes) for elem in l])


@api.route('/esami/', methods=['GET', 'DELETE', 'POST'])
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


@api.route('/esami/<cod_esame>/prove')
@api.route('/prove/<cod_prova>')
def prove(cod_esame=None, cod_prova=None):
    match request.method:
        case 'GET':
            if cod_esame is not None:
                query = select(Prova).where(Prova.cod_esame == cod_esame)
            elif cod_prova is not None:
                query = select(Prova).where(Prova.cod_prova == cod_prova)
            else:
                # TODO magari rendere più bello
                return abort(404)
            prove = db.session.scalars(query).all()
            return jsonify_list(prove, ['anno_accademico', 'docente'])


@api.route('/docenti/<cod_docente>/prove')
def prove_docenti(cod_docente):
    prove = db.session.scalars(select(Prova).where(Prova.cod_docente == cod_docente)).all()
    return jsonify_list(prove)


@api.route('/corsi_laurea')
def corsi_laurea():
    corsi = db.session.scalars(select(CorsoLaurea)).all()
    return jsonify_list(corsi)


@api.route('/appelli', methods=['GET', 'POST'])
def appelli():
    args = request.args
    match request.method:
        case 'GET':
            appelli = db.session.scalars(select(Appello)).all()
            list_appelli = [{'id': appello.cod_prova, 'start': appello.data_appello.isoformat(),
                             'title': appello.prova.esame.nome_corso} for appello in appelli]
            return list_appelli
        case 'POST':
            insert_eventi()
            return '', 204


@api.route('/appelli/info', methods=['GET', 'POST'])
def appelli_table():
    match request.method:
        case 'GET':
            appelli = db.session.scalars(select(Appello)).all()
            return jsonify_list(appelli)
        case 'POST':
            insert_iscrizione_appelli()
            return '', 204


@api.route('/studenti/<matricola>')
def studenti(matricola):
    stud = db.session.scalars(select(Studente).where(Studente.matricola == matricola))
    return jsonify_list(stud)
