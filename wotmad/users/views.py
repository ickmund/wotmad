from hashlib import md5

import requests

from flask import Blueprint
from flask import request, render_template, flash, g, session, redirect, \
    url_for, json


class UserBlueprint(Blueprint):

    def register(self, app, options, first_registration=False):
        super(UserBlueprint, self).register(app, options, first_registration)

        if not first_registration:
            return

        @app.before_request
        def before_request():
            g.user = None
            if 'user_id' in session:
                try:
                    g.user = User.load_user(session['user_id'])
                except User.DoesNotExist:
                    del session['user_id']

blueprint = UserBlueprint('users', __name__)


from wotmad.users.forms import LoginForm
from wotmad.users.models import User
from wotmad.users.decorators import login_required


@blueprint.route('/me/')
@login_required
def profile():
    return render_template("users/profile.html", user=g.user)


@blueprint.route('/logout/')
def logout():
    g.user = None
    del session['user_id']
    flash("Logged out.")
    return redirect(url_for('index'))


@blueprint.route('/login/', methods=['POST'])
def login():
    form = LoginForm(request.form)
    # make sure data are valid, but doesn't validate password is right
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
        session['user_id'] = user.id
        if created:
            # Set a better username
            candidate, _ = email.split('@', 1)

            # See if we have any users with this username already
            qs = User.objects(username__istartswith=candidate)
            if qs.count():
                # Increment the count and shove it on the end of the candidate
                # name
                username = "{0}.{1}".format(candidate, qs.count() + 1)
            else:
                username = candidate

            user.username = username
            user.save()

            # TODO: Redirect to account setup
            flash('Created user. Set your username!')
        else:
            flash('Logged in.')
        return redirect(url_for('index'))

    flash('Login failed.', 'error')
    return redirect(url_for('index'))
