from wotmad import db


class User(db.Document):
    id = db.ObjectIdField()
    email = db.StringField(required=True)
    username = db.StringField(required=True)
    active = db.BooleanField()

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
