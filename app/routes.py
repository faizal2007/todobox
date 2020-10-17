from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'freakie'}
    posts = [
        {
            'author': {'username': 'Jamaluddin'},
            'body' : {'What a beutiful world!!'}
        },
        {
            'author': {'username': 'Rasputin'},
            'body': {'Jomblo happy !!'}
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)