import os
import urllib.parse
from dotenv import load_dotenv
load_dotenv('.flaskenv')

def connect_db(type, app):
    
    DB_URL = os.environ.get('DB_URL')
    DB_USER = os.environ.get('DB_USER')
    # Support both DB_PW and DB_PASSWORD
    DB_PW = os.environ.get('DB_PASSWORD') or os.environ.get('DB_PW')
    DB_NAME = os.environ.get('DB_NAME')
    
    if not all([DB_URL, DB_USER, DB_PW, DB_NAME]):
        raise ValueError('Missing required database environment variables: DB_URL, DB_USER, DB_PASSWORD, DB_NAME')
    
    DB_PW = urllib.parse.quote(DB_PW)

    if type == 'mysql':
        DB_URL = 'mysql://{user}:{pw}@{url}/{db}'.format(user=DB_USER, pw=DB_PW, url=DB_URL, db=DB_NAME)
    elif type == 'postgres':
        DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=DB_USER, pw=DB_PW, url=DB_URL, db=DB_NAME)
    else:
        raise ValueError(f'Unknown database type: {type}')

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL