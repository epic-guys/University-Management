from flask import render_template, request, Blueprint, session, url_for, flash, redirect, abort
from ..models import *
import flask_login
from ..roles import view_role_manager

studenti = Blueprint('studenti', __name__, url_prefix='/studenti')


@studenti.before_request
@view_role_manager.roles(Studente)
def before_request():
    """Used to apply Studente role"""
    pass


@studenti.route('/')
def index():
    return render_template('studenti/dashboard.html')


@studenti.route('/libretto')
def libretto():
    return render_template('studenti/libretto.html')


@studenti.route('/appelli')
def appelli():
    appelli = db.session.scalars(select(Appello)).all()
    return render_template('studenti/appelli.html')


@studenti.route('/appelli/<cod_appello>/iscrizione')
def appello(cod_appello):
    appello = db.session.scalar(select(Appello).where(Appello.cod_appello == cod_appello))
    iscrizioni = db.session.scalars(select(IscrizioneAppello).where(IscrizioneAppello.cod_appello == cod_appello))
    return render_template('studenti/appelli-info.html', appello=appello, iscrizioni=iscrizioni)
