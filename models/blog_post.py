from models.user import User
from google.appengine.ext import ndb

def blog_key(name = 'default'):
    """BlogPost key"""
    return ndb.Key('blogs', name)

class BlogPost(ndb.Model):
    """Contains info about a blog post"""
    subject = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    author = ndb.StructuredProperty(User)
    created = ndb.DateTimeProperty(auto_now_add = True)
    likes = ndb.IntegerProperty(default = 0)
