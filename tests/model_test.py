from app.models import *
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.environ['DB_URI'], echo=False)


def test_utenti():
    with Session(engine) as session:
        print()
        query_persone = select(Persona)
        print(session.execute(query_persone).fetchall())
        print(session.scalars(query_persone).fetchall())


def test_prove():
    with Session(engine) as session:
        print()
        query = select(Appello)
        appelli = session.scalars(query).all()
        for a in appelli: print(a.prova.esame.nome_corso)

def test_appelli():
    with Session(engine) as session:
        print()
        query = select(Appello)
        appelli = session.scalars(query)
        print(appelli.all())


def test_doc():
    with Session(engine) as session:
        d = session.scalar(select(Docente))
        print(d.asdict())


def test_voti():
    with Session(engine) as session:
        print(session.scalars(select(Voto)))
