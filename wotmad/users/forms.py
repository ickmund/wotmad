from flaskext import wtf


class LoginForm(wtf.Form):
    assertion = wtf.HiddenField(validators=[wtf.Required()])


class RegistrationForm(wtf.Form):
    username = wtf.TextField('Username', [wtf.Required()])
