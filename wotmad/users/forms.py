from flask import g

from flaskext import wtf

from wotmad.users.models import User


class LoginForm(wtf.Form):
    assertion = wtf.HiddenField(validators=[wtf.Required()])


USERNAME_REGEX_ERROR = ("Username must begin with a letter and can only "
                        "contain letters and numbers.")


class SetupForm(wtf.Form):
    username = wtf.TextField('Username',
                             [wtf.Required(), wtf.Length(5, 30),
                              wtf.Regexp(r'^[a-zA-Z][a-zA-Z0-9]+$',
                                         message=USERNAME_REGEX_ERROR)])

    def validate_username(self, field):
        """Ensures the username is not already taken"""
        matches = User.objects(username__iexact=field.data, id__ne=g.user.id)
        if matches:
            raise wtf.ValidationError("Username already taken.")
