import flask_login
from sqlalchemy.exc import SQLAlchemyError
import werkzeug.exceptions
from flask import Blueprint, request, jsonify, abort
from .models import *
from .db import db
from sqlalchemy import select, update, delete, insert
from .roles import api_role_manager
from dataclasses import dataclass, fields

api = Blueprint('api', __name__, url_prefix='/api')


@dataclass
class ApiResponse:
    status: str
    message: str
    data: any

    def asdict(self):
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
        }


@api.errorhandler(Exception)
def not_found_handler(e):
    if isinstance(e, werkzeug.exceptions.HTTPException):
        return ApiResponse('Fail', e.description, {}).asdict(), 404

    else:
        return ApiResponse('Error', 'Error on server', e.args).asdict(), 500



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


def jsonify_list(l: list[Model], includes=None):
    return jsonify([elem.asdict(includes) for elem in l])


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
                # Bad request
                return abort(400)
            prove = db.session.scalars(query).all()
            return jsonify_list(prove, ['anno_accademico', 'docente'])


@api.route('/prove/<cod_prova>/appelli')
def appelli_prova(cod_prova):
    query = select(Appello).where(Appello.cod_prova == cod_prova)
    appelli = db.session.scalars(query).all()
    return jsonify_list(appelli)



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


@api.route('/appelli/<cod_appello>/iscrizioni')
def iscrizioni(cod_appello):
    query = select(IscrizioneAppello) \
        .where(IscrizioneAppello.cod_appello == cod_appello)
    return jsonify_list(db.session.scalars(query).all(), ['studente'])


@api.route('/appelli/<cod_appello>/iscrizioni', methods=['POST'])
@api_role_manager.roles(Studente)
def add_iscrizione(cod_appello):
    query = insert(IscrizioneAppello).values({
        'matricola': flask_login.current_user.matricola,
        'cod_appello': cod_appello,
        'data_iscrizione': datetime.now().isoformat()
    })
    db.session.execute(query)
    db.session.commit()
    return '', 204


@api.route('/appelli/info')
def appelli_table():
    if isinstance(flask_login.current_user, Docente):
        appelli = db.session.scalars(select(Appello).where(Appello.prova.cod_docente == flask_login.current_user.cod_docente)).all()
    else:
        appelli = db.session.scalars(select(Appello)).all()
    return jsonify_list(appelli)


@api.route('/voti')
def voti():
    voti = db.session.scalars((select(Voto))).all()
    return jsonify_list(voti)


@api.route('/voti', methods=['POST'])
def add_voti():
    payload = request.json
    for voto in payload:
        try:
            stmt = insert(Voto) \
                    .values(voto)
            db.session.execute(stmt)
        except SQLAlchemyError as e:
            return ApiResponse('Fail', 'Failed to add voto', e.params).asdict(), 400

    db.session.commit()
    return '', 204


@api.route('/voti/<cod_appello>/<matricola>/')
def voto_info(cod_appello, matricola):
    voto = db.session.scalars(select(Voto).where(Voto.cod_appello == cod_appello and Voto.matricola == matricola)).all()
    return jsonify_list(voto)
