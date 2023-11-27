from sqlalchemy import create_engine, select, insert, distinct
from sqlalchemy.orm import Session, Bundle
from dotenv import load_dotenv
from app.models import *
import os

load_dotenv()

engine = create_engine(os.environ['DB_URI'], echo=True)


def test_join():
    with Session(engine) as session:
        query = select(Bundle()).join(IscrizioneAppello).join(Appello)
        print(query)
        for res in session.scalars(query):
            print(res)


def test_anni():
    with Session(engine) as session:
        query = select(AnnoAccademico).where(AnnoAccademico.inizio_anno <= date.today()) \
            .where(date.today() <= AnnoAccademico.fine_anno)
        anni = session.scalars(query).all()
        print(anni)


def test_esameanno_insert():
    with Session(engine) as session:
        # test the insert using a dictionary as input. Use the insert method
        stmt = insert(EsameAnno).values({'cod_esame': 'E1', 'cod_anno_accademico': 2022, 'cod_presidente': '3'})
        session.execute(stmt)
        session.commit()


def test_select_appelli():
    print()
    with Session(engine) as session:
        query = select(Appello).join(Prova).join(Esame) \
            .where(Prova.cod_anno_accademico == 2023) \
            .where(Esame.cod_corso_laurea == 'CT3') \
            .where(Appello.data_appello >= date.today())
        print(query)
        res = session.scalars(query).all()
        for r in res:
            print(r)


def test_select_esiti():
    with Session(engine) as session:
        query = select(IscrizioneAppello, VotoAppello) \
            .outerjoin(VotoAppello) \
            .where(IscrizioneAppello.matricola == '11')
        res = session.execute(query).tuples()
        for r in res:
            print(r)


def test_select_studenti_con_prove():
    with Session(engine) as session:
        query_studenti = select(Studente).join_from(VotoProva, Appello) \
            .join(Prova) \
            .join(Studente) \
            .where(Prova.cod_esame == 'E1') \
            .distinct()
        studenti = session.scalars(query_studenti).all()
        for s in studenti:
            print(s)

