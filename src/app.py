import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sqla

# region App config

db = SQLAlchemy()
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DB_URI']
db.init_app(app)


# endregion

# region Model


class Utente(db.Model):
    __tablename__ = 'utenti'
    id_utente = sqla.Column(sqla.Text, primary_key=True)
    pass_hash = sqla.Column(sqla.Text, nullable=False)


# endregion

# region Routes


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/users')
def get_users():
    users = db.session.execute(db.select(Utente)).scalars()
    return render_template('users.html', users=users)


# endregion

def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
