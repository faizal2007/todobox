from flask import render_template
from app import app, db
from app.models import Todo

@app.route('/')
@app.route('/index')
def index():
    # return ''
    return render_template('index.html')

@app.route('/todo')
def todo():
    # print(app.config)
    return render_template('todo.html')