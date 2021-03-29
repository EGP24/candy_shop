from data import db_session
from os.path import exists
from os import mkdir
from app import app


if not exists('./db'):
    mkdir('./db')
db_session.global_init('db/base.db')

if __name__ == "__main__":
    app.run()