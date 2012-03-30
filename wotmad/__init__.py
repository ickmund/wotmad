from flask import Flask
from flask import render_template

from flaskext.mongoengine import MongoEngine


app = Flask(__name__)
app.config['MONGODB_DB'] = 'wotmad.dev'
app.config['DEBUG'] = True

mongo = MongoEngine(app)


@app.route('/')
def index():
    return render_template("base.html")
