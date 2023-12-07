import flask_login
from sqlalchemy.exc import SQLAlchemyError
import werkzeug.exceptions
from flask import Blueprint, request, abort
from .models import *
from .db import db
from sqlalchemy import select, insert, distinct, func, exists
from .roles import api_role_manager
from dataclasses import dataclass
from typing import ClassVar, TypeVar, Generic
from collections.abc import Iterable

api = Blueprint('api', __name__, url_prefix='/api')


def map_to_dict(model: Iterable[Model] | Model, includes=None):
    if isinstance(model, Iterable):
        return [elem.asdict(includes) for elem in model]
    else:
        return model.asdict(includes)


def format_calendar(appelli: list[Appello]) -> list[dict]:
    list_appelli = [{'id': appello.cod_prova, 'start': appello.data_appello.isoformat(),
                     'title': appello.prova.esame_anno.esame.nome_corso} for appello in appelli]
    return list_appelli

T = TypeVar('T')

@dataclass
class ApiResponse(Generic[T]):
    """
    Classe per rappresentare una risposta dell'API.

    Questa classe è utilizzata per standardizzare le risposte dell'API. Contiene il dato da restituire (se presente), lo stato dell'operazione e un messaggio opzionale.

    Args:
        T: Il tipo di dato da restituire.

    Attributes:
        SUCCESS (str): Stringa che rappresenta lo stato di successo.
        FAIL (str): Stringa che rappresenta lo stato di fallimento.
        ERROR (str): Stringa che rappresenta lo stato di errore.
        data (T): Il dato da restituire. Può essere di qualsiasi tipo.
        status (str): Lo stato dell'operazione. Può essere SUCCESS, FAIL o ERROR.
        message (str, optional): Un messaggio opzionale che fornisce ulteriori dettagli sulla risposta.

    Methods:
        asdict(): Restituisce un dizionario che rappresenta la risposta dell'API.
    """
    SUCCESS: ClassVar[str] = 'success'
    FAIL: ClassVar[str] = 'fail'
    ERROR: ClassVar[str] = 'error'

    data: T = None
    status: str = SUCCESS
    message: str | None = None

    def asdict(self):
        """
        Restituisce un dizionario che rappresenta la risposta dell'API.

        Returns:
            dict: Un dizionario che contiene lo stato, il messaggio e il dato della risposta.
        """
        return {
            'status': self.status,
            'message': self.message,
            'data': self.data
        }


@api.errorhandler(Exception)
def api_error_handler(e):
    if isinstance(e, werkzeug.exceptions.HTTPException):
        return ApiResponse(status=ApiResponse.FAIL, message=e.get_description()).asdict(), 404

    else:
        return ApiResponse(e.args, ApiResponse.FAIL, 'Error on server').asdict(), 500


@api.route('/appelli/')
def appelli():
    """
    Restituisce tutti gli appelli in una lista. Se il parametro 'calendar' è impostato su 'true',
    la lista di appelli viene formattata per essere utilizzata in un calendario.

    Returns:
        list: Una lista di dizionari. Ogni dizionario rappresenta un appello.
              Se 'calendar' è 'true', ogni dizionario contiene 'id', 'start' e 'title'.
              Altrimenti, ogni dizionario contiene tutte le informazioni di un appello
    """
    appelli = db.session.scalars(select(Appello)).all()
    if request.args['calendar'] == 'true':
        list_appelli = format_calendar(appelli)
        return list_appelli
    else:
        appelli = map_to_dict(appelli)
        return ApiResponse(appelli).asdict()


@api.route('/appelli/', methods=['POST'])
@api_role_manager.roles(Docente)
def insert_eventi():
    """
    Inserisce un nuovo evento (appello) nel database.

    Questa funzione richiede che l'utente corrente sia un Docente e che il docente sia il presidente dell'esame o il docente della prova.

    Args:
        req (dict): Un dizionario che rappresenta l'appello da inserire. Deve essere passato nel corpo della richiesta HTTP.

    Returns:
        ApiResponse[None]: Un oggetto ApiResponse che rappresenta la risposta dell'API. Se l'operazione ha successo, ritorna un messaggio di successo.
                     In caso di errore, ritorna un messaggio di errore e un codice di stato HTTP appropriato.

    Raises:
        404: Se la prova specificata nella richiesta non esiste.
        403: Se l'utente corrente non è autorizzato ad aggiungere appelli per la prova specificata.
        400: Se si verifica un errore durante l'inserimento dell'appello nel database.
    """
    req = request.json

    current_docente = flask_login.current_user
    prova = db.session.scalar(select(Prova).where(Prova.cod_prova == req['cod_prova']))
    if prova is None:
        return abort(404, 'Prova not found')

    if (prova.cod_docente != current_docente.cod_docente
            and prova.esame_anno.cod_presidente != current_docente.cod_docente):
        return abort(403, 'Only presidente or prova\'s docente can add appelli')

    try:
        db.session.execute(insert(Appello), req)
        db.session.commit()
    except SQLAlchemyError:
        return ApiResponse(status=ApiResponse.FAIL, message='Failed to add event').asdict(), 400
    return ApiResponse(message='Events inserted successfully').asdict()


@api.route('/esami/')
@api.route('/esami/<cod_esame>')
def esami(cod_esame=None):
    """
    Restituisce tutti gli esami.
    Se viene fornito un codice esame, restituisce solo l'esame corrispondente.

    Args:
        cod_esame (str, optional): Il codice dell'esame da restituire.
        Se non viene fornito, restituisce tutti gli esami.

    Returns:
        ApiResponse[list[Esame]] | ApiResponse[Esame]: ApiResponse che contiene gli esami.
    """
    query = select(Esame).join(EsameAnno)
    if cod_esame is None:
        query = (query.where(EsameAnno.cod_presidente == flask_login.current_user.cod_docente)
                 .where(EsameAnno.cod_anno_accademico == AnnoAccademico.current_anno_accademico().cod_anno_accademico)
                 )
    else:
        query = query.where(Esame.cod_esame == cod_esame)
    esami = db.session.scalars(query).all()
    return ApiResponse(map_to_dict(esami)).asdict()


@api.route('/esami/', methods=['POST'])
@api_role_manager.roles(Docente)
def insert_esami():
    """
    Inserisce un nuovo esame nel database.

    Questa funzione richiede che l'utente corrente sia un Docente.

    Args:
        req (dict): Un dizionario che rappresenta l'esame da inserire.
        Deve essere passato nel corpo della richiesta HTTP.

    Returns:
        ApiResponse[None]: Un oggetto ApiResponse che rappresenta la risposta dell'API.
                     Se l'operazione ha successo, restituisce un messaggio di successo.
                     In caso di errore, restituisce un messaggio di errore e un codice di stato HTTP appropriato.
    """
    db.session.execute(insert(Esame), request.json)
    db.session.commit()
    return ApiResponse(message='Esame inserted successfully').asdict()


@api.route('/corsi_laurea')
def corsi_laurea():
    """
    Restituisce tutti i corsi di laurea.

    Returns:
        ApiResponse[list[CorsoLaurea]]: ApiResponse con la lista di corsi di laurea.
    """
    corsi = db.session.scalars(select(CorsoLaurea)).all()
    return map_to_dict(corsi)


@api.route('/corso_laurea/<cod_corso_laurea>/esami')
def esami_corso_laurea(cod_corso_laurea):
    """
    Restituisce tutti gli esami associati a un corso di laurea.

    Args:
        cod_corso_laurea (str): Il codice del corso di laurea per il quale restituire gli esami.

    Returns:
        ApiResponse[list[Esame]]: ApiResponse con la lista di esami associati al corso di laurea.
    """
    query = select(Esame).where(Esame.cod_corso_laurea == cod_corso_laurea)
    esami = db.session.scalars(query).all()
    return ApiResponse(map_to_dict(esami)).asdict()


@api.route('/esami/<cod_esame>/anni')
def anni_esame(cod_esame):
    """
    Restituisce gli anni accademici associati a un esame.

    Args:
        cod_esame (str): Il codice dell'esame per il quale restituire gli anni accademici.

    Returns:
        ApiResponse[list[EsameAnno]]]: oggetto ApiResponse che contiene una lista di anni accademici
        associati all'esame.
    """
    query = select(EsameAnno).where(EsameAnno.cod_esame == cod_esame)
    esami = db.session.scalars(query).all()
    return ApiResponse(map_to_dict(esami, includes=['anno_accademico', 'presidente'])).asdict()


# TODO candidata da cancellare
@api.route('/corso_laurea/<cod_corso_laurea>/esami_anni')
def esami_anni_corso_laurea(cod_corso_laurea):
    """
    Restituisce gli esami di un anno accademico associati a un corso di laurea.

    Args:
        cod_corso_laurea (str): Il codice del corso di laurea per il quale restituire gli esami.

    Returns:
        ApiResponse[list[EsameAnno]]: ApiResponse che contiene una lista di esami associati
        al corso di laurea per un anno accademico.
    """
    if 'anno_accademico' in request.args:
        query = (select(EsameAnno).where(EsameAnno.cod_corso_laurea == cod_corso_laurea)
                 .where(EsameAnno.cod_anno_accademico == request.args['anno_accademico'])
                 )
    else:
        query = select(EsameAnno).where(EsameAnno.cod_corso_laurea == cod_corso_laurea)

    esami = db.session.scalars(query).all()
    return ApiResponse(map_to_dict(esami, includes=['anno_accademico'])).asdict()


@api.route('/esami/<cod_esame>/prove')
@api.route('/prove/<cod_prova>')
def prove(cod_esame=None, cod_prova=None):
    """
    Restituisce le prove associate a un esame o a una prova specifica.

    Se viene fornito un codice esame, restituisce tutte le prove associate a quell'esame.
    Se viene fornito un codice prova, restituisce la prova corrispondente a quel codice.
    Se non viene fornito nessun codice, restituisce un errore 400.

    Args:
        cod_esame (str, optional): Il codice dell'esame per il quale restituire le prove.
        cod_prova (str, optional): Il codice della prova da restituire.

    Returns:
        ApiResponse[list[Prova]] | ApiResponse[Prova]: ApiResponse che contiene una lista di prove o una singola prova,
        a seconda che sia stato fornito un codice esame o un codice prova.
    """
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


@api.route('/esami/<cod_esame>/prove', methods=['POST'])
@api_role_manager.roles(Docente)
def insert_prove(cod_esame):
    """
    Inserisce una nuova prova per un esame nel database.

    Questa funzione richiede che l'utente corrente sia un Docente e che il docente sia il presidente dell'esame.

    Args:
        cod_esame (str): Il codice dell'esame per il quale inserire la prova.

    Returns:
        ApiResponse[None]: Se l'operazione ha successo, restituisce un messaggio di successo.
                           In caso di errore, restituisce un messaggio di errore e un codice di stato HTTP appropriato.
    """
    esame_stmt = (select(EsameAnno).where(EsameAnno.cod_esame == cod_esame)
                  .where(EsameAnno.cod_anno_accademico == AnnoAccademico.current_anno_accademico().cod_anno_accademico)
                  )
    esame = db.session.scalar(esame_stmt)
    if esame is None:
        abort(404, 'Esame not found')
    if esame.presidente.cod_docente != flask_login.current_user.cod_docente:
        abort(403, 'Only presidente can add prove')

    prova = request.json
    prova['cod_esame'] = cod_esame
    prova['cod_docente'] = flask_login.current_user.cod_docente
    insert_stmt = insert(Prova).values(prova)
    db.session.execute(insert_stmt)
    db.session.commit()
    return ApiResponse(message="Successfully added Prove").asdict()


@api.route('/prove/<cod_prova>/appelli')
def appelli_prova(cod_prova):
    """
    Restituisce tutti gli appelli associati a una prova.

    Args:
        cod_prova (str): Il codice della prova per la quale restituire gli appelli.

    Returns:
        ApiResponse[list[Appello]]: ApiResponse che contiene una lista di appelli associati alla prova.
    """
    query = select(Appello).where(Appello.cod_prova == cod_prova)
    appelli = db.session.scalars(query).all()
    appelli = map_to_dict(appelli)
    return ApiResponse(appelli).asdict()


# TODO candidata da cancellare
@api.route('/docenti/<cod_docente>/prove')
def prove_docenti(cod_docente):
    """
    Restituisce tutte le prove associate a un docente.

    Args:
        cod_docente (str): Il codice del docente per il quale restituire le prove.

    Returns:
        list[Prova]: Lista di prove associate al docente.
    """
    prove = db.session.scalars(select(Prova).where(Prova.cod_docente == cod_docente)).all()
    return map_to_dict(prove)


@api.route('/appelli/<cod_appello>/iscrizioni')
def iscrizioni(cod_appello):
    """
    Restituisce tutte le iscrizioni di un appello.

    Args:
        cod_appello (str): Il codice dell'appello per il quale restituire le iscrizioni.

    Returns:
        ApiResponse[list[IscrizioneAppello]]: ApiResponse che contiene la lista di iscrizioni associate all'appello.
    """
    query = select(IscrizioneAppello).where(IscrizioneAppello.cod_appello == cod_appello)
    res = db.session.scalars(query).all()
    data = map_to_dict(res, ['studente', 'voto_appello'])

    return ApiResponse(data).asdict()


@api.route('/appelli/<cod_appello>/iscrizioni', methods=['POST'])
@api_role_manager.roles(Studente)
def add_iscrizione(cod_appello):
    """
    Aggiunge una nuova iscrizione a un appello.

    Questa funzione richiede che l'utente corrente sia uno Studente.

    Args:
        cod_appello (str): Il codice dell'appello al quale aggiungere l'iscrizione.

    Returns:
        ApiResponse[None]: Se l'operazione ha successo, restituisce un messaggio di successo.
                           In caso di errore, restituisce un messaggio di errore e un codice di stato HTTP appropriato.
    """
    query = insert(IscrizioneAppello).values({
        'matricola': flask_login.current_user.matricola,
        'cod_appello': cod_appello,
        'data_iscrizione': datetime.now().isoformat()
    })
    db.session.execute(query)
    db.session.commit()
    return ApiResponse(message='Successfully added iscrizione').asdict()


# TODO candidata da cancellare
@api.route('/appelli/info')
def appelli_table():
    """
    Restituisce una lista di tutti gli appelli.

    Se l'utente corrente è un Docente, restituisce solo gli appelli associati al docente.

    Returns:
        list[Appello]: Una lista di dizionari. Ogni dizionario rappresenta un appello.
    """
    if isinstance(flask_login.current_user, Docente):
        appelli = db.session.scalars(
            select(Appello).join(Prova).where(Prova.cod_docente == flask_login.current_user.cod_docente)).all()
    else:
        appelli = db.session.scalars(select(Appello)).all()
    return map_to_dict(appelli)


@api.route('/appelli/<cod_appello>/voti')
def voti(cod_appello):
    """
    Restituisce tutti i voti associati a un appello.

    Args:
        cod_appello (str): Il codice dell'appello per il quale restituire i voti.

    Returns:
        list[VotoAppello]: Lista di voti associati all'appello.
    """
    query = select(VotoAppello).where(VotoAppello.cod_appello == cod_appello)
    voti = db.session.scalars(query).all()
    return map_to_dict(voti)


@api.route('/appelli/<cod_appello>/voti', methods=['POST'])
@api_role_manager.roles(Docente)
def add_voti(cod_appello):
    """
    Aggiunge nuovi voti a un appello.

    Questa funzione richiede che l'utente corrente sia un Docente.

    Args:
        cod_appello (str): Il codice dell'appello al quale aggiungere i voti.

    Returns:
        ApiResponse[None]: Se l'operazione ha successo, restituisce un messaggio di successo.
                           In caso di errore, restituisce un messaggio di errore e un codice di stato HTTP appropriato.
    """
    voti = request.json
    for voto in voti:
        voto['cod_appello'] = cod_appello
    try:
        stmt = insert(VotoAppello).values(voti)
        db.session.execute(stmt)
    except SQLAlchemyError as e:
        return ApiResponse(e.args, ApiResponse.FAIL, 'Failed to add voto').asdict(), 400

    db.session.commit()
    return ApiResponse(message='Successfully added voti').asdict()


@api.route('/esami/<cod_esame>/prove/voti')
def get_voti_prove(cod_esame):
    """
    Restituisce le situazioni con le prove associate a un esame.
    Precisamente, si restituiscono delle righe con le seguenti informazioni:
    - codice prova
    - codice appello (se presente)
    - matricola studente
    - voto prova (se presente)

    Uno studente viene preso in considerazione solo se ha passato almneo una prova dell'esame.
    In tal caso, vengono restituite tutte le prove dell'esame associalte a lui, con il voto se presente
    e il codice appello.


    Args:
        cod_esame (str): Il codice dell'esame per il quale restituire i voti.

    Returns:
        list[dict]: Ogni dizionario rappresenta una riga della situazione.
    """
    """
    -- query corrispondente
    SELECT p.cod_prova, v.*
    FROM studenti s
    CROSS JOIN prove p
    LEFT JOIN esami e ON e.cod_esame = p.cod_esame
    LEFT JOIN voti_prove v ON v.cod_prova = p.cod_prova AND v.matricola = s.matricola
    WHERE p.cod_esame = $cod_esame
    AND s.matricola IN (
        SELECT DISTINCT v.matricola
        FROM voti_prove v
        JOIN prove p ON p.cod_prova = v.cod_prova
        WHERE p.cod_esame = $cod_esame
        );
    """
    fn = (
        func.get_voti_prove_esame(cod_esame)
        .table_valued('cod_appello', 'matricola', 'voto')
    )
    query = select(fn)
    res = db.session.execute(query).mappings().all()
    res = [
        {key: value for key, value in row.items()}
        for row in res
    ]
    return ApiResponse(res).asdict()


def get_voti_prove_studente(cod_esame, matricola):
    """
    Restituisce la situazione di un esame di uno singolo studente.

    Args:
        cod_esame (str): Il codice dell'esame per il quale restituire i voti.
        matricola (str): La matricola dello studente per il quale restituire i voti.

    Returns:
        list[tuple[VotoProva, Prova]]: Ogni tupla rappresenta una riga della situazione.
        La tupla contiene il voto della prova e la prova stessa.
    """
    esame = db.session.scalar(select(Esame).where(Esame.cod_esame == cod_esame))
    if esame is None:
        raise Exception('Esame not found')
    studente = db.session.scalar(select(Studente).where(Studente.matricola == matricola))
    if studente is None:
        raise Exception('Studente not found')

    """
    -- Query corrispondente
    SELECT v.*
    FROM voti_prove v
    JOIN appelli a ON v.cod_appello = a.cod_appello
    RIGHT JOIN prove p ON a.cod_prova = p.cod_prova
        AND v.matricola = $matricola
    WHERE p.cod_esame = $cod_esame;
    """
    query = (
        select(VotoProva, Prova)
        .join(VotoProva.appello)
        .outerjoin(Appello.prova.and_(VotoProva.matricola == matricola), full=True)
        .where(Prova.cod_esame == cod_esame)
    )
    return db.session.execute(query).tuples()


# TODO aggiungere anno accademico
@api.route('/esami/<cod_esame>/prove/voti/<matricola>')
def voti_prove(cod_esame, matricola):
    """
    Restituisce tutte le prove associate a un esame e uno studente,
    con il voto se presente.
    """

    try:
        voti = get_voti_prove_studente(cod_esame, matricola)
    except:
        return ApiResponse(status=ApiResponse.FAIL, message='Failed to get voti').asdict(), 400

    """
    Cosa fa? Molto divertente:
    - per ogni tupla (voto, prova) crea un nuovo dizionario partendo da prova
    - aggiunge al dizionario il voto, se presente, altrimenti None
    - aggiunge il dizionario alla lista
    Amo Python
    """
    voti_payload = [
        dict(prova.asdict(), voto=(None if voto is None else voto.asdict()))
        for voto, prova in voti
    ]
    return ApiResponse(voti_payload).asdict()


@api.route('/esami/<cod_esame>/studenti')
def studenti_candidati(cod_esame):
    """
    Restituisce gli studenti che hanno sostenuto almeno una prova dell'esame.

    Args:
        cod_esame (str): Il codice dell'esame per il quale restituire gli studenti.

    Returns:
        list[Studente]: Lista di studenti che hanno sostenuto almeno una prova dell'esame.
    """
    query = (
        select(distinct(Studente))
        .join(VotoProva)
        .join(Appello)
        .join(Prova)
        .where(Prova.cod_esame == cod_esame)
    )

    return db.session.scalars(query).all()


@api.route('/esami/<cod_esame>/anni/<cod_anno_accademico>/idonei')
def idonei_voto(cod_esame, cod_anno_accademico):
    """
    Restituisce gli studenti che hanno sostenuto tutte le prove dell'esame.

    Args:
        cod_esame (str): Il codice dell'esame per il quale restituire gli studenti.
        cod_anno_accademico (str): Il codice dell'anno accademico per il quale restituire gli studenti.

    Returns:
        ApiResponse[list[Studente]]: ApiResponse con lista di studenti che hanno sostenuto tutte le prove dell'esame.
    """

    fn = (
        func.get_voti_prove_esame(cod_esame, cod_anno_accademico)
        .table_valued('cod_prova', 'cod_appello', 'matricola', 'voto')
    )

    query = (
        select(Studente, VotoEsame)
        .where(Studente.matricola.in_(
            select(fn.c.matricola)
            .select_from(fn)
            .group_by('matricola')
            .having(func.count('*') == func.count(fn.c.cod_appello))
        ))
        .outerjoin(VotoEsame)
    )

    res = db.session.execute(query).all()
    serialized_list = []
    for studente, voto in res:
        serialized = studente.asdict()
        serialized['voto'] = voto.asdict() if voto is not None else None
        serialized_list.append(serialized)
    return ApiResponse(serialized_list).asdict()


@api.route('/appelli/<cod_appello>/voti/<matricola>/')
def voto_info(cod_appello, matricola):
    """
    Restituisce il voto di uno studente per un appello.

    Args:
        cod_appello (str): Il codice dell'appello per il quale restituire il voto.
        matricola (str): La matricola dello studente per il quale restituire il voto.

    Returns:
        list[VotoAppello]: Lista di voti dello studente per l'appello.
    """
    voto = db.session.scalars(
        select(VotoAppello).where(VotoAppello.cod_appello == cod_appello and VotoAppello.matricola == matricola)).all()
    return map_to_dict(voto)


@api.route('/studenti/libretto')
@api_role_manager.roles(Studente)
def libretto():
    """
    Restituisce il libretto dello studente corrente.

    Returns:
        ApiResponse[list[dict]]: ApiResponse con il libretto.
    """
    studente: Studente = flask_login.current_user
    query = select(Esame, VotoEsame) \
        .outerjoin(VotoEsame, VotoEsame.cod_esame == Esame.cod_esame) \
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
    """
    Restituisce tutti i tipi di prova.

    Returns:
        list[TipoProva]: ApiResponse con la lista di tipi di prova.
    """
    tipi_prova = db.session.scalars(select(TipoProva)).all()
    return map_to_dict(tipi_prova)


@api.route('/esami/<cod_esame>/anni/<cod_anno_accademico>/voti', methods=['POST'])
@api_role_manager.roles(Docente)
def add_voti_esame(cod_esame, cod_anno_accademico):
    """
    Aggiunge nuovi voti a un esame.

    Questa funzione richiede che l'utente corrente sia un Docente e che il docente sia il presidente dell'esame.

    Args:
        cod_esame (str): Il codice dell'esame al quale aggiungere i voti.
        cod_anno_accademico (str): Il codice dell'anno accademico per il quale aggiungere i voti.

    Returns:
        ApiResponse[None]: Se l'operazione ha successo, restituisce un messaggio di successo.
                           In caso di errore, restituisce un messaggio di errore e un codice di stato HTTP appropriato.
    """
    esame = db.session.scalar(
        select(EsameAnno).where(EsameAnno.cod_esame == cod_esame)
        .where(EsameAnno.cod_anno_accademico == cod_anno_accademico)
    )
    if esame is None:
        raise Exception('Esame not found')
    if esame.cod_presidente != flask_login.current_user.cod_docente:
        raise Exception('Only presidente can add voti')

    data_completamento = datetime.now().isoformat()

    voti = request.json
    for voto in voti:
        voto['cod_esame'] = cod_esame
        voto['cod_anno_accademico'] = cod_anno_accademico
        voto['data_completamento'] = data_completamento
    try:
        stmt = insert(VotoEsame).values(voti)
        db.session.execute(stmt)
    except SQLAlchemyError as e:
        return ApiResponse(e.args, ApiResponse.FAIL, 'Failed to add voto').asdict(), 400

    db.session.commit()
    return ApiResponse(message='Successfully added voti').asdict()


@api.route('/appelli/prossimi')
@api_role_manager.roles(Studente)
def prossimi_appelli():
    """
    Restituisce tutti gli appelli di esami non ancora superati.

    Questa funzione richiede che l'utente corrente sia uno Studente.

    Returns:
        ApiResponse[list[Appello]]: ApiResponse con la lista di appelli.
    """

    """
    -- Query corrispondente
    SELECT a.*
    FROM appelli a
    NATURAL JOIN prove p
    WHERE NOT EXISTS (
        SELECT *
        FROM voti_esami v
        WHERE v.cod_esame = p.cod_esame
        AND v.matricola = $matricola
    );
    """

    studente = flask_login.current_user
    query = (
        select(Appello)
        .join(Prova)
        .where(~exists(
            select(VotoEsame)
            .where(VotoEsame.cod_esame == Prova.cod_esame)
            .where(VotoEsame.matricola == studente.matricola)
        ))
    )

    appelli = db.session.scalars(query).all()

    if request.args['calendar'] == 'true':
        list_appelli = format_calendar(appelli)
        return list_appelli

    return ApiResponse(map_to_dict(appelli)).asdict()
