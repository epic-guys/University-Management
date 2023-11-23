from sqlalchemy import create_engine, select, insert
from sqlalchemy.orm import Session, Bundle
from dotenv import load_dotenv
from app.models import *
import os

load_dotenv()

engine = create_engine(os.environ['DB_URI'], echo=False)


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


def test_select():
    with Session(engine) as session:
        query = select(EsameAnno).where(EsameAnno.cod_esame == 'E1')
        print()
        print(str(query))
        esame = session.scalars(query).fetchall()
        print(esame)
        for e in esame:
            print(e.cod_anno_accademico)
