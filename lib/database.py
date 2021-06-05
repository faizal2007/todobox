import os
import urllib.parse

# def connect_postgres(app):
#     """
#     Postgres configuration
#     varible need to be declare at in env 
#     export DB_USER="postgres"
#     or .flaskenv
#     """
#     DB_URL=os.environ.get('DB_URL')
#     DB_USER=os.environ.get('DB_USER')
#     DB_PW=os.environ.get('DB_PW')
#     DB_NAME=os.environ.get('DB_NAME')

#     DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=DB_USER,pw=urllib.parse.quote(DB_PW),url=DB_URL,db=DB_NAME)

#     app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

# def connect_mysql(app):
    
#     DB_URL=os.environ.get('DB_URL')
#     DB_USER=os.environ.get('DB_USER')
#     DB_PW=os.environ.get('DB_PW')
#     DB_NAME=os.environ.get('DB_NAME')

#     DB_URL = 'mysql://{user}:{pw}@{url}/{db}'.format(user=DB_USER,pw=urllib.parse.quote(DB_PW),url=DB_URL,db=DB_NAME)

#     app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

def connect_db(type, app):
    
    DB_URL=os.environ.get('DB_URL')
    DB_USER=os.environ.get('DB_USER')
    DB_PW=os.environ.get('DB_PW')
    DB_NAME=os.environ.get('DB_NAME')

    if type == 'mysql':
        DB_URL = 'mysql://{user}:{pw}@{url}/{db}'.format(user=DB_USER,pw=urllib.parse.quote(DB_PW),url=DB_URL,db=DB_NAME)
    elif type == 'postgres':
        DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=DB_USER,pw=urllib.parse.quote(DB_PW),url=DB_URL,db=DB_NAME)
    else:
        print('Wrong database type.')

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL