import json
import datetime

from sqlalchemy import ForeignKey
from .db import db
import sqlalchemy as sqla


class Persona(db.Model):
    __tablename__ = 'persone'
    cod_persona = sqla.Column(sqla.Text, primary_key=True)
    nome = sqla.Column(sqla.Text)
    cognome = sqla.Column(sqla.Text)
    data_nascita = sqla.Column(sqla.Date)
    sesso = sqla.Column(sqla.Text)
    email = sqla.Column(sqla.Text)
    password_hash = sqla.Column(sqla.Text)
    ruolo = sqla.Column(sqla.Text)

    def __init__(self, cod_persona: str, nome: str, cognome: str, data_nascita: datetime.date, sesso: str, email: str, password_hash: str, ruolo: str):
        self.cod_persona = cod_persona
        self.nome = nome
        self.cognome = cognome
        self.data_nascita = data_nascita
        self.sesso = sesso
        self.email = email
        self.password_hash = password_hash
        self.ruolo = ruolo

    def to_json(self):
        return json.dumps(self.__dict__)


class Docente(Persona):
    __tablename__ = 'docenti'
    cod_docente = sqla.Column(sqla.Text, ForeignKey(Persona.cod_persona), primary_key=True)

    def __init__(self, cod_docente: str, nome: str, cognome: str, data_nascita: datetime.date, sesso: str, email: str, password_hash: str, ruolo: str):
        super().__init__(cod_docente, nome, cognome, data_nascita, sesso, email, password_hash, ruolo)
        self.cod_docente = cod_docente

    def to_json(self):
        return json.dumps(self.__dict__)


class Studente(Persona):
    __tablename__ = 'studenti'
    matricola = sqla.Column(sqla.Text, ForeignKey(Persona.cod_persona), primary_key=True)

    def __init__(self, matricola: str, nome: str, cognome: str, data_nascita: datetime.date, sesso: str, email: str, password_hash: str, ruolo: str):
        super().__init__(matricola, nome, cognome, data_nascita, sesso, email, password_hash, ruolo)
        self.matricola = matricola

    def to_json(self):
        return json.dumps(self.__dict__)


class Esame(db.Model):
    __tablename__ = 'esami'
    cod_esame = sqla.Column(sqla.Text, primary_key=True)
    nome_corso = sqla.Column(sqla.Text)
    anno = sqla.Column(sqla.Integer)
    cfu = sqla.Column(sqla.Integer)

    def __init__(self, cod_esame: str, nome_corso: str, anno: int, cfu: int):
        self.cod_esame = cod_esame
        self.nome_corso = nome_corso
        self.anno = anno
        self.cfu = cfu

    def to_json(self):
        return json.dumps(self.__dict__)


class Prova(Esame):
    __tablename__ = 'prove'
    cod_prova = sqla.Column(sqla.Text, primary_key=True)
    scadenza = sqla.Column(sqla.Date)
    cod_esame = sqla.Column(sqla.Text, ForeignKey(Esame.cod_esame))

    def __init__(self, cod_esame: str, nome_corso: str, anno: int, cfu: int, cod_prova: str, scadenza: datetime.date):
        super().__init__(cod_esame, nome_corso, anno, cfu)
        self.cod_prova = cod_prova
        self.scadenza = scadenza

    def to_json(self):
        return json.dumps(self.__dict__)


class Appello(Prova):
    data = sqla.Column(sqla.Date, primary_key=True)
    cod_prova = sqla.Column(sqla.Text, ForeignKey(Prova.cod_prova))

    def __init__(self, cod_esame: str, nome_corso: str, anno: int, cfu: int, cod_prova: str, scadenza: datetime.date, data: datetime.date):
        super().__init__(cod_esame, nome_corso, anno, cfu, cod_prova, scadenza)
        self.data = data

    def to_json(self):
        return json.dumps(self.__dict__)

