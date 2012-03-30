from flask import Flask
from flask import g, request, render_template, jsonify

from flaskext import mongoengine
from flaskext import login
from flaskext import wtf

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
        # Do the actual browserid login here
        return "Assertion: {0}".format(assertion)

    return jsonify(form.errors)


@auth.user_loader
def load_user_from_mongo(userid):
    """Accepts a unicode representation of a userid and returns a User object
    or None."""
    try:
        return User.load_user(id=userid)
    except User.DoesNotExist:
        return None
