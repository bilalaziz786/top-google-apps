from google.appengine.ext import db


class TopApps(db.Model):
    app_id = db.StringProperty(multiline=True)
    description = db.StringProperty(multiline=True)
    developer = db.StringProperty(multiline=True)
    developer_id = db.StringProperty(multiline=True)
    free = db.BooleanProperty(indexed=False)
    full_price = db.StringProperty(multiline=True)
    icon = db.StringProperty(multiline=True)
    price = db.StringProperty(multiline=True)
    score = db.StringProperty(multiline=True)
    title = db.StringProperty(multiline=True)
    url = db.StringProperty(multiline=True)
    use = db.BooleanProperty()
