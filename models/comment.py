from google.appengine.ext import ndb
from user import User

class Comment(ndb.Model):
    """comment info"""
    post_id = ndb.IntegerProperty(required = True)
    content = ndb.StringProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.StructuredProperty(User)
