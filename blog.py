## Contains entities for saving to app engine

import os
import re
import codecs
import hashlib
import hmac
import random
import string
import webapp2
import jinja2

from blog_users import User
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

class Like(ndb.Model):
    """likes by users"""
    post_id = ndb.IntegerProperty(required = True)
    author = ndb.StructuredProperty(User)


class Comment(ndb.Model):
    """comment info"""
    post_id = ndb.IntegerProperty(required = True)
    content = ndb.StringProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    author = ndb.StructuredProperty(User)
