import json
from datetime import date, datetime
from .db import db
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, ForeignKeyConstraint, select
from flask_login import UserMixin
from flask_roles import RoleMixin


class Model(db.Model):
    __abstract__ = True

    def asdict(self, includes=None):
        if includes is None:
            includes = []

        d = {
            col.key: getattr(self, col.key)
            if not isinstance(getattr(self, col.key), date)
            else getattr(self, col.key).isoformat()
            # Se si usa __table__ invece di __mapper__ restituisce solo le colonne della tabella Docenti senza Persone
            for col in self.__mapper__.columns
        }
        for attr in includes:
            d[attr] = getattr(self, attr)
            if d[attr] is not None:
                d[attr] = d[attr].asdict()
        return d

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

    def asdict(self, includes=None):
        d = super().asdict(includes)
        del d['password_hash']
        return d

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

    def full_name(self):
        return self.nome + ' ' + self.cognome

    def get_id(self):
        """Necessario per Flask_Login"""
        return self.cod_persona


class Docente(Persona):
    __tablename__ = 'docenti'
    cod_docente: Mapped[str] = mapped_column(ForeignKey('persone.cod_persona'), primary_key=True)
    prove: Mapped[list['Prova']] = relationship(back_populates='docente')

    # relazioni
    esami_anni: Mapped[list['EsameAnno']] = relationship(back_populates='presidente')

    __mapper_args__ = {
        'polymorphic_identity': 'D'
    }

    def __init__(self, cod_docente: str, nome: str, cognome: str, data_nascita: date, sesso: str, email: str,
                 password_hash: str, ruolo: str):
        super().__init__(cod_docente, nome, cognome, data_nascita, sesso, email, password_hash, ruolo)
        self.cod_docente = cod_docente


class Studente(Persona):
    __tablename__ = 'studenti'
    matricola: Mapped[str] = mapped_column(ForeignKey('persone.cod_persona'), primary_key=True)
    cod_corso_laurea: Mapped[str] = mapped_column(ForeignKey('corsi_laurea.cod_corso_laurea'))
    cod_anno_iscrizione: Mapped[int] = mapped_column(ForeignKey('anni_accademici.cod_anno_accademico'))

    __mapper_args__ = {
        'polymorphic_identity': 'S'
    }

    # relazioni
    corso_laurea: Mapped['CorsoLaurea'] = relationship(back_populates='studenti')
    anno_iscrizione: Mapped['AnnoAccademico'] = relationship()

    def __init__(self, matricola: str, nome: str, cognome: str, data_nascita: date, sesso: str, email: str,
                 password_hash: str, ruolo: str):
        super().__init__(matricola, nome, cognome, data_nascita, sesso, email, password_hash, ruolo)
        self.matricola = matricola


class AnnoAccademico(Model):
    __tablename__ = 'anni_accademici'

    cod_anno_accademico: Mapped[int] = mapped_column(primary_key=True)
    anno_accademico: Mapped[str] = mapped_column()
    inizio_anno: Mapped[date] = mapped_column()
    fine_anno: Mapped[date] = mapped_column()

    @classmethod
    def current_anno_accademico(cls):
        today = date.today()
        query = select(AnnoAccademico).where(AnnoAccademico.inizio_anno <= today,
                                             AnnoAccademico.fine_anno >= today)
        return db.session.scalar(query)


class CorsoLaurea(Model):
    __tablename__ = 'corsi_laurea'

    cod_corso_laurea: Mapped[str] = mapped_column(primary_key=True)
    nome_corso_laurea: Mapped[str] = mapped_column()
    esami: Mapped[list['Esame']] = relationship(back_populates='corso_laurea')
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

    # relazioni
    esami_anni: Mapped[list['EsameAnno']] = relationship(back_populates='esame')

    def __init__(self, cod_esame: str, nome_corso: str, anno: int, cfu: int):
        self.cod_esame = cod_esame
        self.nome_corso = nome_corso
        self.anno = anno
        self.cfu = cfu



class EsameAnno(Model):
    __tablename__ = 'esami_anni_accademici'

    cod_anno_accademico: Mapped[str] = mapped_column(
        ForeignKey('anni_accademici.cod_anno_accademico'),
        primary_key=True
    )
    cod_esame: Mapped[str] = mapped_column(ForeignKey('esami.cod_esame'), primary_key=True)
    cod_presidente: Mapped[str] = mapped_column(ForeignKey('docenti.cod_docente'))

    # relazioni
    prove: Mapped[list['Prova']] = relationship(back_populates='esame_anno')
    anno_accademico: Mapped[AnnoAccademico] = relationship()
    presidente: Mapped[Docente] = relationship(back_populates='esami_anni')
    esame: Mapped[Esame] = relationship(back_populates='esami_anni')


class Prova(Model):
    __tablename__ = 'prove'

    cod_prova: Mapped[str] = mapped_column(primary_key=True)
    tipo_prova: Mapped[str] = mapped_column(ForeignKey('tipi_prove.tipo_prova'))
    denominazione_prova: Mapped[str] = mapped_column()
    descrizione_prova: Mapped[str] = mapped_column()
    peso: Mapped[float] = mapped_column()
    scadenza: Mapped[date] = mapped_column()
    cod_esame: Mapped[str] = mapped_column(ForeignKey('esami.cod_esame'))
    cod_docente: Mapped[str] = mapped_column(ForeignKey('docenti.cod_docente'))
    cod_anno_accademico: Mapped[int] = mapped_column(ForeignKey('anni_accademici.cod_anno_accademico'))

    # relazioni
    esame_anno: Mapped[EsameAnno] = relationship(foreign_keys=[cod_anno_accademico, cod_esame], back_populates='prove')
    appelli: Mapped[list['Appello']] = relationship(back_populates='prova')
    docente: Mapped[Docente] = relationship(back_populates='prove')
    esame: Mapped[Esame] = relationship()
    anno_accademico: Mapped[AnnoAccademico] = relationship()

    __table_args__ = (
        ForeignKeyConstraint(
            ['cod_anno_accademico', 'cod_esame'],
            ['esami_anni_accademici.cod_anno_accademico', 'esami_anni_accademici.cod_esame']
        ),
    )


class Appello(Model):
    __tablename__ = 'appelli'

    cod_appello: Mapped[str] = mapped_column(primary_key=True)
    data_appello: Mapped[datetime] = mapped_column()
    cod_prova: Mapped[str] = mapped_column(ForeignKey('prove.cod_prova'))
    aula: Mapped[str] = mapped_column()

    # relazioni
    prova: Mapped[Prova] = relationship(back_populates='appelli')

    def __init__(self, prova: Prova, data_appello: datetime, aula: str):
        self.cod_prova = prova.cod_prova
        self.prova = prova
        self.data_appello = data_appello
        self.aula = aula


class IscrizioneAppello(Model):
    __tablename__ = 'iscrizioni_appelli'

    cod_appello: Mapped[str] = mapped_column(ForeignKey('appelli.cod_appello'), primary_key=True)
    matricola: Mapped[str] = mapped_column(ForeignKey('studenti.matricola'), primary_key=True)
    data_iscrizione: Mapped[datetime] = mapped_column()

    # Relationships
    studente: Mapped[Studente] = relationship()
    appello: Mapped[Appello] = relationship()
    voto_appello: Mapped['VotoAppello'] = relationship(back_populates='iscrizione_appello')


class VotoAppello(Model):
    __tablename__ = 'voti_appelli'

    cod_appello: Mapped[str] = mapped_column(ForeignKey('appelli.cod_appello'), primary_key=True)
    matricola: Mapped[str] = mapped_column(ForeignKey('studenti.matricola'), primary_key=True)
    voto: Mapped[int] = mapped_column()

    __table_args__ = (
        ForeignKeyConstraint(
            ['cod_appello', 'matricola'],
            ['iscrizioni_appelli.cod_appello', 'iscrizioni_appelli.matricola']
        ),
    )

    # relazioni
    iscrizione_appello: Mapped[IscrizioneAppello] = relationship(back_populates='voto_appello')
    appello: Mapped[Appello] = relationship()
    studente: Mapped[Studente] = relationship()

    def __init__(self, voto: int):
        self.data = Appello.data
        self.cod_prova = Appello.cod_prova
        self.matricola = Studente.matricola
        self.voto = voto


class VotoProva(Model):
    __tablename__ = 'voti_prove'

    cod_appello: Mapped[str] = mapped_column(ForeignKey('appelli.cod_appello'), primary_key=True)
    matricola: Mapped[str] = mapped_column(ForeignKey('studenti.matricola'), primary_key=True)
    voto: Mapped[int] = mapped_column()

    __table_args__ = (
        ForeignKeyConstraint(
            ['cod_appello', 'matricola'],
            ['iscrizioni_appelli.cod_appello', 'iscrizioni_appelli.matricola']
        ),
    )

    # relazioni
    iscrizioneAppello: Mapped[IscrizioneAppello] = relationship()
    studente: Mapped[Studente] = relationship()
    appello: Mapped[Appello] = relationship()


class VotoEsame(Model):
    __tablename__ = 'voti_esami'

    cod_esame: Mapped[str] = mapped_column(ForeignKey('esami.cod_esame'), primary_key=True)
    matricola: Mapped[str] = mapped_column(ForeignKey('studenti.matricola'), primary_key=True)
    cod_anno_accademico: Mapped[int] = mapped_column(ForeignKey('anni_accademici.cod_anno_accademico'))
    voto: Mapped[int] = mapped_column()
    data_completamento: Mapped[date] = mapped_column()

    __table_args__ = (
        ForeignKeyConstraint(
            ['cod_esame', 'cod_anno_accademico'],
            ['esami_anni_accademici.cod_esame', 'esami_anni_accademici.cod_anno_accademico']
        ),
    )

    # relazioni
    studente: Mapped[Studente] = relationship()
    esameAnno: Mapped[EsameAnno] = relationship(foreign_keys=[cod_anno_accademico, cod_esame])


class TipoProva(Model):
    __tablename__ = 'tipi_prove'

    tipo_prova: Mapped[str] = mapped_column(primary_key=True)

    def __init__(self, tipo_prova: str):
        self.tipo_prova = tipo_prova
