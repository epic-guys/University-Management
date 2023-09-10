import json
from datetime import date
from .db import db
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin
from flask_roles import RoleMixin


class Model(db.Model):
    __abstract__ = True

    def to_dict(self):
        return {
            col.key: getattr(self, col.key) if not isinstance(getattr(self, col.key), date) else getattr(self,col.key).isoformat()
            for col in self.__table__.columns
        }

    @classmethod
    def from_json(cls, obj: str | dict):
        if isinstance(obj, str):
            obj = json.loads(obj)
        return cls(**obj)


class Persona(Model, UserMixin, RoleMixin):
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
    prove: Mapped[list['Prova']] = relationship(back_populates='docente')

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
    cod_corso_laurea: Mapped[str] = mapped_column(ForeignKey('corsi_laurea.cod_corso_laurea'))
    corso_laurea: Mapped['CorsoLaurea'] = relationship(back_populates='studenti')

    __mapper_args__ = {
        'polymorphic_identity': 'S'
    }

    def __init__(self, matricola: str, nome: str, cognome: str, data_nascita: date, sesso: str, email: str,
                 password_hash: str, ruolo: str):
        super().__init__(matricola, nome, cognome, data_nascita, sesso, email, password_hash, ruolo)
        self.matricola = matricola


class CorsoLaurea(Model):
    __tablename__ = 'corsi_laurea'

    cod_corso_laurea: Mapped[str] = mapped_column(primary_key=True)
    nome_corso_laurea: Mapped[str] = mapped_column()
    esami: Mapped['Esame'] = relationship(back_populates='corso_laurea')
    studenti: Mapped[list[Studente]] = relationship(back_populates='corso_laurea')


class Esame(Model):
    __tablename__ = 'esami'
    cod_esame: Mapped[str] = mapped_column(primary_key=True)
    nome_corso: Mapped[str] = mapped_column()
    descrizione_corso: Mapped[str] = mapped_column()
    anno: Mapped[int] = mapped_column()
    cfu: Mapped[int] = mapped_column()
    cod_corso_laurea: Mapped[str] = mapped_column(ForeignKey('corsi_laurea.cod_corso_laurea'))
    corso_laurea: Mapped[CorsoLaurea] = relationship(back_populates='esami')
    prove: Mapped[list['Prova']] = relationship(back_populates='esame')

    def __init__(self, cod_esame: str, nome_corso: str, anno: int, cfu: int):
        self.cod_esame = cod_esame
        self.nome_corso = nome_corso
        self.anno = anno
        self.cfu = cfu


class Prova(Model):
    __tablename__ = 'prove'
    cod_prova: Mapped[str] = mapped_column(primary_key=True)
    tipo_prova: Mapped[str] = mapped_column()
    descrizione_prova: Mapped[str] = mapped_column()
    scadenza: Mapped[date] = mapped_column()
    cod_esame: Mapped[str] = mapped_column(ForeignKey('esami.cod_esame'))
    esame: Mapped[Esame] = relationship(back_populates='prove')
    appelli: Mapped[list['Appello']] = relationship(back_populates='prova')
    cod_docente: Mapped[str] = mapped_column(ForeignKey('docenti.cod_docente'))
    docente: Mapped[Docente] = relationship(back_populates='prove')

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
