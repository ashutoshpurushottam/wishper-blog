## helper functions and convenience code
## for saving blog users

import hashlib
import hmac
import random
import string
import re

from google.appengine.ext import ndb
from base.secret_code import secret as SECRET

# username regex
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# password regex
PWD_RE = re.compile(r"^.{3,20}$")
# email regex
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

def valid_username(username):
    """Checks if username is valid"""
    return USER_RE.match(username)

def valid_password(password):
    """Checks if password is valid"""
    return PWD_RE.match(password)

def valid_email(email):
    """Checks if email is valid"""
    return EMAIL_RE.match(email)

def hash_str(s):
    """based on HMAC"""
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    """a secure value using hash"""
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    """Checks if h is a valid secure value"""
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

def make_salt():
    """Makes a salt for password hashing"""
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    """Hashes password"""
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    """Checks hash of password and its validity"""
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)

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


