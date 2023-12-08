import flask_login
from flask import render_template, request, Blueprint, abort
from ..models import *
from ..roles import view_role_manager
from sqlalchemy import select, insert, distinct

docenti = Blueprint('docenti', __name__, url_prefix='/docenti')


@docenti.before_request
@view_role_manager.roles(Docente)
def before_request():
    """Used to apply Docente role"""
    pass


@docenti.route('/')
def index():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina principale.
    """
    return render_template('docenti/dashboard.html')


@docenti.route('/corsi-laurea')
def corsi_laurea():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina dei corsi di laurea.
    Esegue una query per ottenere tutti i corsi di laurea.
    Invia i corsi di laurea alla pagina HTML.
    """
    corsi = db.session.scalars(select(CorsoLaurea)).all()
    return render_template('docenti/corsi-laurea.html', corsi=corsi)


@docenti.route('/corsi-laurea/<cod_corso_laurea>')
def corso_laurea(cod_corso_laurea):
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina di un corso di laurea.
    Esegue una query per ottenere il corso di laurea.
    Invia il corso di laurea alla pagina HTML.
    """
    corso = db.session.scalar(select(CorsoLaurea).where(CorsoLaurea.cod_corso_laurea == cod_corso_laurea))
    return render_template('docenti/corso-laurea.html', corso=corso)


@docenti.route('/esami/')
@docenti.route('/esami/<cod_esame>')
@docenti.route('/esami/<cod_esame>/anni/<cod_anno_accademico>')
def esami(cod_esame=None, cod_anno_accademico=None):
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina degli esami.
    Esegue una query e valuta i parametri per ottenere gli esami.
    Controlla se ci sono parametri per ottenere gli esami di un anno accademico specifico.
    Invia gli esami alla pagina HTML.
    """
    if cod_esame is None:
        return render_template('docenti/esami.html')

    q = select(EsameAnno).where(EsameAnno.cod_esame == cod_esame)
    if cod_anno_accademico is None:
        q = q.where(EsameAnno.cod_anno_accademico == AnnoAccademico.current_anno_accademico().cod_anno_accademico)
    else:
        q = q.where(EsameAnno.cod_anno_accademico == cod_anno_accademico)
    esame_anno = db.session.scalar(q)
    if esame_anno is None:
        return abort(404)

    return render_template('docenti/esame.html', esameanno=esame_anno)


@docenti.route('/prove/<cod_prova>')
def prove(cod_prova):
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina delle prove.
    Esegue una query per ottenere la prova.
    Invia la prova alla pagina HTML.
    """
    query = select(Prova).where(Prova.cod_prova == cod_prova)
    prova = db.session.scalar(query)
    if prova is None:
        return abort(404)

    return render_template('docenti/prova.html', prova=prova)


@docenti.route('/esami/<cod_esame>/anni/<cod_anno_accademico>/voti', methods=['GET', 'POST'])
def voti(cod_esame, cod_anno_accademico):
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina dei voti.
    Esegue una query per ottenere uno specifico esame anno.
    Invia l'esame anno alla pagina HTML.
    """
    esameanno = db.session.scalar(select(EsameAnno)
                              .where(EsameAnno.cod_esame == cod_esame)
                              .where(EsameAnno.cod_anno_accademico == cod_anno_accademico)
                              )
    if esameanno is None:
        return abort(404)
    return render_template('docenti/voti.html', esameanno=esameanno)


@docenti.route('/appelli/')
def appelli():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina degli appelli.
    Esegue una query per ottenere gli appelli di cui il docente è responsabile.
    Invia gli appelli alla pagina HTML.
    """
    current_user: Docente = flask_login.current_user
    anno = AnnoAccademico.current_anno_accademico()
    query = select(Appello).join(Prova).join(Esame) \
        .where(Prova.cod_anno_accademico == anno.cod_anno_accademico) \
        .where(Prova.cod_docente == current_user.cod_docente)
    appelli = db.session.scalars(query).all()
    return render_template('docenti/appelli.html', appelli=appelli)


@docenti.route('/appelli/<cod_appello>')
def appello(cod_appello):
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina di un appello.
    Esegue una query per ottenere l'appello.
    Invia l'appello alla pagina HTML.
    """
    appello = db.session.scalar(select(Appello).where(Appello.cod_appello == cod_appello))
    iscrizioni = db.session.scalars(select(IscrizioneAppello).where(IscrizioneAppello.cod_appello == cod_appello))
    return render_template('docenti/appello.html', appello=appello, iscrizioni=iscrizioni)


@docenti.route('/profilo')
def profilo():
    """
    Questa funzione viene chiamata quando un utente tenta di accedere alla pagina del profilo di un docente.
    Invia il docente alla pagina HTML.
    """
    user = flask_login.current_user
    return render_template('docenti/profilo.html', user=user)
