import json
import datetime

from .login import login_manager
from .db import db
import sqlalchemy as sqla


class Persona(db.Model):
    __tablename__ = 'persone'
    cod_persona = sqla.Column(sqla.Text, primary_key=True)
    nome = sqla.Column(sqla.Text)
    cognome = sqla.Column(sqla.Text)
    data_nascita = sqla.Column(sqla.Date)
    sesso = sqla.Column(sqla.Text)

    def __init__(self, cod_persona: str, nome: str, cognome: str, data_nascita: datetime.date, sesso: str):
        self.cod_persona = cod_persona
        self.nome = nome
        self.cognome = cognome
        self.data_nascita = data_nascita
        self.sesso = sesso

    def to_json(self):
        return json.dumps(self.__dict__)


