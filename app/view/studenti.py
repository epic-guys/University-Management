from flask import render_template, request, Blueprint, abort, current_app
from ..models import *
import flask_login
from ..roles import view_role_manager
from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError

studenti = Blueprint('studenti', __name__, url_prefix='/studenti')


@studenti.before_request
@view_role_manager.roles(Studente)
def before_request():
    """Used to apply Studente role"""
    pass


@studenti.route('/')
def index():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina principale.
    """
    return render_template('studenti/dashboard.html')


@studenti.route('/libretto')
def libretto():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina del libretto.
    """
    return render_template('studenti/libretto.html')


@studenti.route('/appelli/')
def appelli():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina degli appelli.
    Esegue una query per ottenere gli appelli che devono ancora essere svolti.
    Invia gli appelli alla pagina HTML.
    """
    current_user: Studente = flask_login.current_user
    anno = AnnoAccademico.current_anno_accademico()
    query = select(Appello).join(Prova).join(Esame) \
        .where(Prova.cod_anno_accademico == anno.cod_anno_accademico) \
        .where(Esame.cod_corso_laurea == current_user.cod_corso_laurea) \
        .where(Appello.data_appello >= datetime.now())

    appelli = db.session.scalars(query).all()
    return render_template('studenti/appelli.html', appelli=appelli)


@studenti.route('/appelli/<cod_appello>', methods=['GET', 'POST'])
def appello(cod_appello):
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina di un appello.
    Esegue una query per ottenere un appello passato come parametro e un'altra per ottenere le varie iscrizioni agli appelli.
    Invia l'appello e le iscrizioni alla pagina HTML.
    Se l'utente tenta di iscriversi all'appello, viene eseguita una query per aggiungere l'iscrizione.
    """
    if request.method == 'GET':
        appello = db.session.scalar(select(Appello).where(Appello.cod_appello == cod_appello))
        if appello is None:
            return abort(404)
        iscrizioni = db.session.scalars(select(IscrizioneAppello).where(IscrizioneAppello.cod_appello == cod_appello))
        return render_template('studenti/appello.html', appello=appello, iscrizioni=iscrizioni)

    else:
        studente: Studente = flask_login.current_user
        params = {
            'matricola': studente.matricola,
            'cod_appello': cod_appello,
            'data_iscrizione': datetime.now()
        }
        try:
            query = insert(IscrizioneAppello).values(params)
            db.session.execute(query)
        except SQLAlchemyError as e:
            db.session.rollback()
            return abort(500, e)

        db.session.commit()
        return 'Iscritto correttamente'


@studenti.route('/esiti')
def esiti():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina degli esiti.
    Esegue una query per ottenere gli esiti di uno studente.
    Invia gli esiti alla pagina HTML.
    """
    studente: Studente = flask_login.current_user
    query = select(IscrizioneAppello, VotoAppello) \
        .outerjoin(VotoAppello) \
        .where(IscrizioneAppello.matricola == studente.matricola)
    # Restituisce una lista di tuple associando così le iscrizioni ai voti, se ci sono
    # Mi raccomando il .all(), mi ha fatto bestemmiare per un'ora
    iscrizioni_voti = db.session.execute(query).tuples().all()
    for t in iscrizioni_voti:
        current_app.logger.info(t)
    return render_template('studenti/esiti.html', iscrizioni_voti=iscrizioni_voti)

@studenti.route('/profilo')
def profilo():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina del profilo di uno studente.
    Invia lo studente alla pagina HTML.
    """
    user = flask_login.current_user
    return render_template('studenti/profilo.html',user=user)
