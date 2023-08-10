from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.environ['SECRET_KEY']
SQLALCHEMY_DATABASE_URI = os.environ['DB_URI']
