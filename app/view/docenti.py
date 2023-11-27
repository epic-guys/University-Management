from flask import render_template, request, Blueprint, session, url_for, flash, redirect, abort
from ..models import *
import flask_login
from ..roles import view_role_manager


docenti = Blueprint('docenti', __name__, url_prefix='/docenti')


@docenti.before_request
@view_role_manager.roles(Docente)
def before_request():
    """Used to apply Docente role"""
    pass


@docenti.route('/')
def index():
    return render_template('docenti/dashboard.html')


@docenti.route('/corsi-laurea')
def corsi_laurea():
    corsi = db.session.scalars(select(CorsoLaurea)).all()
    return render_template('docenti/corsi-laurea.html', corsi=corsi)


@docenti.route('/corsi-laurea/<cod_corso_laurea>')
def corso_laurea(cod_corso_laurea):
    corso = db.session.scalar(select(CorsoLaurea).where(CorsoLaurea.cod_corso_laurea == cod_corso_laurea))
    return render_template('docenti/corso-laurea.html', corso=corso)


@docenti.route('/esami/')
@docenti.route('/esami/<cod_esame>')
@docenti.route('/esami/<cod_esame>/anni/<cod_anno_accademico>')
def esami(cod_esame=None, cod_anno_accademico=None):
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
    query = select(Prova).where(Prova.cod_prova == cod_prova)
    prova = db.session.scalar(query)
    if prova is None:
        return abort(404)

    return render_template('docenti/prova.html', prova=prova)


@docenti.route('/voti/')
def voti():
    return render_template('docenti/voti.html')


@docenti.route('/voti/<cod_appello>/<matricola>/')
def voti_info(cod_appello, matricola):
    voto = db.session.scalars(select(VotoAppello).where(VotoAppello.cod_appello == cod_appello and VotoAppello.matricola == matricola))
    return render_template('docenti/voto-info.html', voto=voto)


@docenti.route('/appelli/')
def appelli():
    current_user: Docente = flask_login.current_user
    anno = AnnoAccademico.current_anno_accademico()
    query = select(Appello).join(Prova).join(Esame) \
        .where(Prova.cod_anno_accademico == anno.cod_anno_accademico) \


    appelli = db.session.scalars(query).all()
    return render_template('docenti/appelli.html', appelli=appelli)

@docenti.route('/appelli/<cod_appello>')
def appello(cod_appello):
    appello = db.session.scalar(select(Appello).where(Appello.cod_appello == cod_appello))
    iscrizioni = db.session.scalars(select(IscrizioneAppello).where(IscrizioneAppello.cod_appello == cod_appello))
    return render_template('docenti/appello.html', appello=appello, iscrizioni=iscrizioni)


@docenti.route('/profilo')
def profilo():
    user = flask_login.current_user
    return render_template('docenti/profilo.html',user=user)
