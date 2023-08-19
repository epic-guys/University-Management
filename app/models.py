import inspect
import json
from datetime import date
from .db import db
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, inspect
from flask_login import UserMixin


class JSONSerializable:
    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, obj: str | dict):
        raise NotImplementedError()


class Model(db.Model, JSONSerializable):
    __abstract__ = True


class Persona(Model, UserMixin):
    __tablename__ = 'persone'

    ruolo: Mapped[str] = mapped_column()
    cod_persona: Mapped[str] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column()
    cognome: Mapped[str] = mapped_column()
    data_nascita: Mapped[date] = mapped_column()
    sesso: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    password_hash: Mapped[str] = mapped_column()

    __mapper_args__ = {
        'polymorphic_identity': 'persona',
        'polymorphic_on': 'ruolo'
    }

    def __init__(self, cod_persona: str, nome: str, cognome: str, data_nascita: date, sesso: str, email: str,
                 password_hash: str, ruolo: str):
        self.cod_persona = cod_persona
        self.nome = nome
        self.cognome = cognome
        self.data_nascita = data_nascita
        self.sesso = sesso
        self.email = email
        self.password_hash = password_hash
        self.ruolo = ruolo

    def get_id(self):
        """Necessario per Flask_Login"""
        return self.cod_persona


class Docente(Persona):
    __tablename__ = 'docenti'
    cod_docente: Mapped[str] = mapped_column(ForeignKey('persone.cod_persona'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'D'
    }

    def __init__(self, cod_docente: str, nome: str, cognome: str, data_nascita: date, sesso: str, email: str,
                 password_hash: str, ruolo: str):
        super().__init__(cod_docente, nome, cognome, data_nascita, sesso, email, password_hash, ruolo)
        self.cod_docente = cod_docente

    def to_json(self):
        return json.dumps(self.__dict__)


class Studente(Persona):
    __tablename__ = 'studenti'
    matricola: Mapped[str] = mapped_column(ForeignKey('persone.cod_persona'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'S'
    }

    def __init__(self, matricola: str, nome: str, cognome: str, data_nascita: date, sesso: str, email: str,
                 password_hash: str, ruolo: str):
        super().__init__(matricola, nome, cognome, data_nascita, sesso, email, password_hash, ruolo)
        self.matricola = matricola


class Esame(Model):
    __tablename__ = 'esami'
    cod_esame: Mapped[str] = mapped_column(primary_key=True)
    nome_corso: Mapped[str] = mapped_column()
    anno: Mapped[int] = mapped_column()
    cfu: Mapped[int] = mapped_column()
    prove: Mapped[list['Prova']] = relationship(back_populates='esame')

    def __init__(self, cod_esame: str, nome_corso: str, anno: int, cfu: int):
        self.cod_esame = cod_esame
        self.nome_corso = nome_corso
        self.anno = anno
        self.cfu = cfu

    @classmethod
    def from_json(cls, obj: str | dict):
        inspector = inspect(db.engine)
        columns = inspector.get_columns(Esame)
        # TODO STO ANCORA FACENDO CHIEDO SCUSA, QUESTO LANCERÀ UN'ECCEZIONE
        super().from_json(cls), obj


class Prova(Model):
    __tablename__ = 'prove'
    cod_prova: Mapped[str] = mapped_column(primary_key=True)
    scadenza: Mapped[date] = mapped_column()
    cod_esame: Mapped[str] = mapped_column(ForeignKey('esami.cod_esame'))
    esame: Mapped[Esame] = relationship(back_populates='prove')
    appelli: Mapped[list['Appello']] = relationship(back_populates='prova')

    def __init__(self, esame: Esame, cod_prova: str, scadenza: date):
        self.cod_prova = cod_prova
        self.cod_esame = esame.cod_esame
        self.esame = esame
        self.scadenza = scadenza


class Appello(Model):
    data: Mapped[date] = mapped_column(primary_key=True)
    cod_prova: Mapped[str] = mapped_column(ForeignKey('prove.cod_prova'), primary_key=True)
    prova: Mapped[Prova] = relationship(back_populates='appelli')

    def __init__(self, prova: Prova, data: date):
        self.cod_prova = prova.cod_prova
        self.prova = prova
        self.data = data
