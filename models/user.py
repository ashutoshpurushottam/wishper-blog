## helper functions and convenience code
## for saving blog users

import hashlib
import hmac
import random
import string
import re

from google.appengine.ext import ndb
from base.secret_code import secret as SECRET
from base.helpers import make_pw_hash

def users_key(group = 'default'):
    """Defines a key for User"""
    return ndb.Key('users', group)

class User(ndb.Model):
    """Contains info about a user"""
    username = ndb.StringProperty(required = True)
    pwd_hashed = ndb.StringProperty(required = True)
    email = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


def store_blog_user(username, password, email):
    """
    if username/password do not match with existing user then create
    a new user in the db. Else, return a error response string.
    """
    error = ""
    common_username_user = User.gql("WHERE username='%s'" % username).get()
    common_email_user = User.gql("WHERE email='%s'" % email).get()

    if(not common_username_user) and (not common_email_user):
        user = User(username=username, pwd_hashed=make_pw_hash(username, password), parent = users_key())
        key = user.put()
        if not key:
            error = "Error in database. Please try after some time."
    else:
        if common_username_user and common_email_user:
            error = "The username and email already exist! Select another username and email."
        elif common_username_user:
            error = "The username already exists! Please select another username."
        elif common_email_user:
            error = "The email is already in use! Please select another email."

    return error


