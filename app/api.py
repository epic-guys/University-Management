import dataclasses

import flask_login
from sqlalchemy.exc import SQLAlchemyError
import werkzeug.exceptions
from flask import Blueprint, request, abort
from .models import *
from .db import db
from sqlalchemy import select, update, delete, insert
from .roles import api_role_manager
from dataclasses import dataclass
from typing import ClassVar
from collections.abc import Iterable

api = Blueprint('api', __name__, url_prefix='/api')


def map_to_dict(model: Iterable[Model] | Model, includes=None):
    if isinstance(model, Iterable):
        return [elem.asdict(includes) for elem in model]
    else:
        return model.asdict(includes)


@dataclass
class ApiResponse:
    SUCCESS: ClassVar[str] = 'success'
    FAIL: ClassVar[str] = 'fail'
    ERROR: ClassVar[str] = 'error'

    # Non mi fa mettere {} come default
    data: any = dataclasses.field(default_factory=dict)
    status: str = SUCCESS
    message: str | None = None

    def asdict(self):
        return {
            'status': self.status,
            'message': self.message,
            'data': self.data
        }


@api.errorhandler(Exception)
def not_found_handler(e):
    if isinstance(e, werkzeug.exceptions.HTTPException):
        return ApiResponse(None, ApiResponse.FAIL).asdict(), 404

    else:
        return ApiResponse(e.args, ApiResponse.FAIL, 'Error on server').asdict(), 500


def insert_esame():
    # TODO opportuna sanificazione dell'input
    db.session.execute(insert(Esame), request.form.to_dict())
    db.session.commit()
    return ApiResponse(message='Esame inserted successfully').asdict()


def delete_esame(cod):
    """
    TODO pure qua sanificare, sarebbe ancora più bello magari far sì che gli
    esami non si elimino dal database ma si "annullano", in modo da gestire
    un ipotetico annullamento dell'esame.
    """
    db.session.execute(delete(Esame).where(Esame.cod_esame == cod))


def insert_eventi():
    # TODO sanificare input
    req = request.form.to_dict()
    req['data_appello'] = req['data'] + 'T' + req['ora']
    req.pop('data', 'ora')
    db.session.execute(insert(Appello), req)
    db.session.commit()
    return ApiResponse(message='Events inserted successfully').asdict()


@api.route('/esami/', methods=['GET', 'DELETE', 'POST'])
@api.route('/esami/<cod_esame>', methods=['GET'])
def esami(cod_esame=None):
    match request.method:
        case 'GET':
            query = select(EsameAnno)
            if cod_esame is not None:
                query = query.where(EsameAnno.cod_esame == cod_esame)
            query = query.where(EsameAnno.cod_anno_accademico == AnnoAccademico.current_anno_accademico().cod_anno_accademico)
            esami = db.session.scalars(query).all()
            return ApiResponse(map_to_dict(esami)).asdict()
        case 'POST':
            return insert_esame()
        case 'DELETE':
            return delete_esame(cod_esame)


@api.route('/esami/corso_laurea/<cod_corso_laurea>')
def esami_corso_laurea(cod_corso_laurea):
    query = select(EsameAnno).where(Esame.cod_corso_laurea == cod_corso_laurea) \
        .where(EsameAnno.cod_anno_accademico == AnnoAccademico.current_anno_accademico().cod_anno_accademico)
    esami = db.session.scalars(query).all()
    return ApiResponse(map_to_dict(esami)).asdict()


@api.route('/esami/<cod_esame>/prove', methods=['GET', 'POST'])
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
            prove = map_to_dict(prove, ['anno_accademico', 'docente'])
            return ApiResponse(prove).asdict()
        case 'POST':
            esame_stmt = select(EsameAnno).where(EsameAnno.cod_esame == cod_esame) \
                .where(EsameAnno.cod_anno_accademico == AnnoAccademico.current_anno_accademico().cod_anno_accademico)
            esame = db.session.scalar(esame_stmt)
            if esame is None:
                abort(404, 'Esame not found')
            if esame.presidente.cod_docente != flask_login.current_user.cod_docente:
                abort(403, 'Only presidente can add prove')

            prova = request.json
            insert_stmt = insert(Prova).values(prova)
            db.session.execute(insert_stmt)
            db.session.commit()
            return ApiResponse(None, message="Successfully added Prove")


@api.route('/prove/<cod_prova>/appelli')
def appelli_prova(cod_prova):
    query = select(Appello).where(Appello.cod_prova == cod_prova)
    appelli = db.session.scalars(query).all()
    appelli = map_to_dict(appelli)
    return ApiResponse(appelli).asdict()


@api.route('/docenti/<cod_docente>/prove')
def prove_docenti(cod_docente):
    prove = db.session.scalars(select(Prova).where(Prova.cod_docente == cod_docente)).all()
    return map_to_dict(prove)


@api.route('/corsi_laurea')
def corsi_laurea():
    corsi = db.session.scalars(select(CorsoLaurea).join(Esame).join(Prova).where(
        Prova.cod_docente == flask_login.current_user.cod_docente)).all()
    return map_to_dict(corsi)


@api.route('/appelli/', methods=['GET', 'POST'])
def appelli():
    match request.method:
        case 'GET':
            appelli = db.session.scalars(select(Appello)).all()
            if request.args['calendar'] == 'true':
                list_appelli = [{'id': appello.cod_prova, 'start': appello.data_appello.isoformat(),
                             'title': appello.prova.esame.nome_corso} for appello in appelli]
                return list_appelli
            else:
                appelli = map_to_dict(appelli)
                return ApiResponse(appelli).asdict()
        case 'POST':
            return insert_eventi()


@api.route('/appelli/<cod_appello>/iscrizioni', methods=['GET', 'POST'])
def iscrizioni(cod_appello):
    if request.method == 'GET':
        query = select(IscrizioneAppello) \
            .where(IscrizioneAppello.cod_appello == cod_appello)
        res = db.session.scalars(query).all()
        data = map_to_dict(res, ['studente'])

        return ApiResponse(data).asdict()

    elif request.method == 'POST':
        query = insert(IscrizioneAppello).values({
            'matricola': flask_login.current_user.matricola,
            'cod_appello': cod_appello,
            'data_iscrizione': datetime.now().isoformat()
        })
        db.session.execute(query)
        db.session.commit()
        return ApiResponse(message='Successfully added iscrizione').asdict()


@api.route('/appelli/info')
def appelli_table():
    if isinstance(flask_login.current_user, Docente):
        appelli = db.session.scalars(
            select(Appello).join(Prova).where(Prova.cod_docente == flask_login.current_user.cod_docente)).all()
    else:
        appelli = db.session.scalars(select(Appello)).all()
    return map_to_dict(appelli)


@api.route('/voti')
def voti():
    voti = db.session.scalars((select(VotoAppello))).all()
    return map_to_dict(voti)


@api.route('/voti', methods=['POST'])
def add_voti():
    payload = request.json
    for voto in payload:
        try:
            stmt = insert(VotoAppello) \
                .values(voto)
            db.session.execute(stmt)
        except SQLAlchemyError as e:
            return ApiResponse(e.params, ApiResponse.FAIL, 'Failed to add voto').asdict(), 400

    db.session.commit()
    return '', 204


@api.route('/voti/<cod_appello>/<matricola>/')
def voto_info(cod_appello, matricola):
    voto = db.session.scalars(select(VotoAppello).where(VotoAppello.cod_appello == cod_appello and VotoAppello.matricola == matricola)).all()
    return map_to_dict(voto)


@api.route('/studenti/libretto')
@api_role_manager.roles(Studente)
def libretto():
    studente: Studente = flask_login.current_user
    query = select(Esame, VotoEsame) \
        .outerjoin(VotoEsame)
    # esami = studente.corso_laurea.esami
    # esami = map_to_dict(esami)
    esami = db.session.execute(query).all()
    serialized_list = []
    for esame, voto in esami:
        serialized = esame.asdict()
        serialized['voto'] = voto.asdict() if voto is not None else None
        serialized_list.append(serialized)
    return ApiResponse(serialized_list).asdict()


@api.route('/tipi-prova')
def tipi_prova():
    tipi_prova = db.session.scalars(select(TipoProva)).all()
    return map_to_dict(tipi_prova)