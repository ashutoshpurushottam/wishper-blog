from google.appengine.ext import ndb
from user import User

class Like(ndb.Model):
    """likes by users"""
    post_id = ndb.IntegerProperty(required = True)
    author = ndb.StructuredProperty(User)
