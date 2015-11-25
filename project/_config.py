import os

basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = "flasktaskr.db"
USER = "admin"
PASSWORD = "admin"

WTF_CSRF_ENABLED = True
SECRET_KEY = "my_secret"

DATABASE_PATH = os.path.join(basedir, DATABASE)