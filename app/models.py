import json

from .login import login_manager
from .db import db
import sqlalchemy as sqla


class Utente(db.Model):
    __tablename__ = 'utenti'
    id_utente = sqla.Column(sqla.Text, primary_key=True)
    pass_hash = sqla.Column(sqla.Text, nullable=False)

    def __int__(self, id_utente: str, pass_hash: str):
        self.id_utente = id_utente
        self.pass_hash = pass_hash

    def to_json(self):
        return json.dumps(self.__dict__)


@login_manager.user_loader
def user_loader(username):
    return Utente('lmao', 'cock')
