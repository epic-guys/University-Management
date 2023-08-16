from app.models import Persona, Studente, Docente
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.environ['DB_URI'], echo=False)


def test_utenti():
    with Session(engine) as session:
        query_persone = select(Persona)
        print()
        print(session.execute(query_persone).fetchall())

