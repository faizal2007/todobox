import os
import urllib.parse
from dotenv import load_dotenv
load_dotenv('.flaskenv')

def connect_db(type, app):
    
    DB_URL=os.environ.get('DB_URL')
    DB_USER=os.environ.get('DB_USER')
    DB_PW=urllib.parse.quote(os.environ.get('DB_PW'))
    DB_NAME=os.environ.get('DB_NAME')
    print(DB_PW)

    if type == 'mysql':
        DB_URL = 'mysql://{user}:{pw}@{url}/{db}'.format(user=DB_USER,pw=DB_PW,url=DB_URL,db=DB_NAME)
    elif type == 'postgres':
        DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=DB_USER,pw=DB_PW,url=DB_URL,db=DB_NAME)
    else:
        print('Wrong database type.')

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL