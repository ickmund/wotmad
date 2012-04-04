from wotmad import db


class User(db.Document):
    id = db.ObjectIdField()
    email = db.StringField(required=True)
    username = db.StringField(required=True)
    is_active = db.BooleanField()

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return u'<User: {0}'.format(self.email)

    def __unicode__(self):
        return unicode(self.username)

    def __str__(self):
        return self.__unicode__()

    @classmethod
    def load_user(klass, id):
        return klass.objects.get(id=id)
