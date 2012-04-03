from flask import render_template

from wotmad import app
from wotmad.users.forms import LoginForm


@app.route('/')
def index():
    form = LoginForm()
    return render_template("base.html", form=form)
