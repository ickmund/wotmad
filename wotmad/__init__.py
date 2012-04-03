from flask import Flask

from flaskext import mongoengine


app = Flask(__name__)
app.config['MONGODB_DB'] = 'wotmad-dev'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '0xdeadbeef'

db = mongoengine.MongoEngine(app)


from wotmad.views import * # noqa

from wotmad.users.views import blueprint as users_blueprint
app.register_blueprint(users_blueprint, url_prefix='/users')
