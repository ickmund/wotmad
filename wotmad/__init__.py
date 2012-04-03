from hashlib import md5

from flask import Flask
from flask import g, request, flash, url_for, redirect
from flask import json
from flask import render_template, jsonify

from flaskext import mongoengine
from flaskext import login
from flaskext import wtf

import requests


app = Flask(__name__)
app.config['MONGODB_DB'] = 'wotmad-dev'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '0xdeadbeef'


mongo = mongoengine.MongoEngine(app)
auth = login.LoginManager()
auth.setup_app(app)


# MODELS {{{

def get_object_or_None(klass, *args, **kwargs):
    try:
        return klass.objects.get(*args, **kwargs)
    except klass.DoesNotExist:
        return None


class User(mongo.Document):
    id = mongo.ObjectIdField()
    email = mongo.StringField(required=True)
    username = mongo.StringField(required=True)
    active = mongo.BooleanField()

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return u'<User: {0}'.format(self.email)

    def __unicode__(self):
        return unicode(self.email)

    def __str__(self):
        return self.__unicode__()

    @classmethod
    def load_user(klass, id):
        return klass.objects.get(id=id)

# END MODELS }}}


# FORMS {{{

class LoginForm(wtf.Form):
    assertion = wtf.HiddenField(validators=[wtf.Required()])

# END FORMS }}}


@app.route('/')
def index():
    form = LoginForm()
    return render_template("base.html", form=form)


@app.route('/accounts/login/', methods=["POST"])
def do_login():
    form = LoginForm()
    if form.validate_on_submit():
        assertion = form.data['assertion']
        # XXX: Is this the best way to load the audience?
        # Should probably be in the settings..
        audience = request.url_root.rstrip('/')
        # Do the actual browserid login here
        payload = dict(assertion=assertion, audience=audience)
        print "Verifying with payload: {0!r}".format(payload)

        req = requests.post('https://browserid.org/verify', data=payload,
                            verify=True)
        try:
            result = json.loads(req.content)
        except ValueError:
            return "Error connecting with BrowserID", 500

        if result['status'] != 'okay':
            return "Error validating login: {0}".format(result), 500

        email = result['email']

        # Get or create the user
        defaults = dict(username=md5(email).hexdigest(), active=False)
        user, created = User.objects.get_or_create(email=email,
                                                   defaults=defaults)

        login.login_user(user, remember=True)

        flash("Logged in.", 'success')
        return redirect(url_for('index'))

    return jsonify(form.errors)


@app.route('/accounts/logout/')
def do_logout():
    login.logout_user()
    flash("Logged out", 'success')
    return redirect(url_for('index'))


@auth.user_loader
def load_user_from_mongo(userid):
    """Accepts a unicode representation of a userid and returns a User object
    or None."""
    try:
        return User.load_user(id=userid)
    except User.DoesNotExist:
        return None
