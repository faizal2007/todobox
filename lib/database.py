import os

def connect_postgres(app):
    """
    Postgres configuration
    varible need to be declare at in env 
    export POSTGRES_USER="postgres"
    or .flaskenv
    """
    POSTGRES_URL=os.environ.get('POSTGRES_URL')
    POSTGRES_USER=os.environ.get('POSTGRES_USER')
    POSTGRES_PW=os.environ.get('POSTGRES_PW')
    POSTGRES_DB=os.environ.get('POSTGRES_DB')

    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL