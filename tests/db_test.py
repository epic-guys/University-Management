from sqlalchemy import create_engine, select
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