from mongoengine import *

class MongoPhotographer(Document):
    interests = ListField(StringField(max_length=30))
    last_name = StringField(max_length=120, required=True)
    display_name = StringField(max_length=120, required=True)
    first_name = StringField(max_length=120, required=True)

