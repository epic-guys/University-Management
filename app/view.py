from flask import render_template, request, Blueprint, session, url_for, flash, redirect, abort
from .models import *
import flask_login
from .roles import view_role_manager

view = Blueprint('view', __name__)
studenti = Blueprint('studenti', __name__, url_prefix='/studenti')
docenti = Blueprint('docenti', __name__, url_prefix='/docenti')


view.register_blueprint(studenti)
view.register_blueprint(docenti)


@studenti.before_request
@view_role_manager.roles(Studente)
def before_request():
    """Used to apply Studente role"""
    pass


@docenti.before_request
@view_role_manager.roles(Docente)
def before_request():
    """Used to apply Docente role"""
    pass


@studenti.route('/')
def index():
    return render_template('studenti/dashboard.html')


@studenti.route('/libretto')
def libretto():
    return render_template('studenti/libretto.html')


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


@view.route('/appelli')
def appelli():
    if isinstance(flask_login.current_user,Docente):
        return render_template('docenti/appelli_docenti.html')
    else:
        return render_template('studenti/appelli_studenti.html')


@docenti.route('/appelli/<cod_appello>')
def appello(cod_appello):
    appello = db.session.scalar(select(Appello).where(Appello.cod_appello == cod_appello))
    iscrizioni = db.session.scalars(select(IscrizioneAppello).where(IscrizioneAppello.cod_appello == cod_appello))
    return render_template('docenti/appello.html', appello=appello, iscrizioni=iscrizioni)

@studenti.route('/appelli/<cod_appello>/iscrizione')
def appello(cod_appello):
    appello = db.session.scalar(select(Appello).where(Appello.cod_appello == cod_appello))
    iscrizioni = db.session.scalars(select(IscrizioneAppello).where(IscrizioneAppello.cod_appello == cod_appello))
    return render_template('studenti/appelli-info.html', appello=appello, iscrizioni=iscrizioni)

@flask_login.login_required
@view.route('/')
def index():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('view.login'))
    if isinstance(flask_login.current_user, Docente):
        return redirect(url_for('view.docenti.index'))
    else:
        return redirect(url_for('view.studenti.index'))


@view.route('/users')
def get_users():
    users = db.session.execute(db.select(Persona)).scalars()
    return render_template('users.html', users=users)


@view.route('/login', methods=['GET', 'POST'])
def login():
    if not flask_login.current_user.is_authenticated:
        if request.method == 'GET':
            return render_template('login.html')

        email = request.form['email']
        password = request.form['password']
        # TODO CAMBIARE ASSOLUTAMENTE IN PASSWORD HASH, TEST
        query = select(Persona).where(Persona.email == email and Persona.password_hash == password)
        user = db.session.scalar(query)
        if user is not None:
            flask_login.login_user(user)
        else:
            flash("No user found")
            return render_template('login.html')

    return redirect(url_for('view.index'))


@view.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('view.index'))



@view.route('/profilo')
def profilo():
    user = flask_login.current_user
    return render_template('studenti/profilo.html',user=user)
