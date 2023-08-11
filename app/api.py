from flask import Blueprint
from .models import Persona
from .db import db

api = Blueprint('api', __name__)

users = [
    {
        'first_name': 'paolo',
        'last_name': 'brosio'
    },
    {
        'first_name': 'dio',
        'last_name': 'mio'
    }
]


