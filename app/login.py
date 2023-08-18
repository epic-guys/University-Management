from flask_login import LoginManager
from .db import db
from .models import Persona

login_manager = LoginManager()


@login_manager.user_loader
def load_user(cod_persona: str) -> Persona:
    query = db.select(Persona).where(Persona.cod_persona == cod_persona)
    res = db.session.scalars(query)
    """
    Flask-Login vuole che il metodo load_user restituisca l'oggetto utente
    se viene trovato o None se non viene trovato. Il metodo first fa
    esattamente questa cosa con le righe del risultato della query.
    """
    return res.first()
