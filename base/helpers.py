import re
import hmac
import random
import string
import hashlib

from secret_code import secret as SECRET

def validate_name(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return USER_RE.match(username)

def validate_password(password):
    PASS_RE = re.compile(r"^.{3,20}$")
    return PASS_RE.match(password)

def validate_email(email):
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
    return not email or EMAIL_RE.match(email)

def hash_str(val):
    """create hash for input string"""
    return hmac.new(SECRET, val).hexdigest()


def make_secure_val(val):
	"""
	Creates a hash value separated with pipe.
	To verify that the cookie has not been
	tampered with.
	"""
	return "%s|%s" %(val, hash_str(val))

def check_secure_val(h):
    """test if secure_val and its hash are correct"""
    test = h.split("|")[0]
    if h == make_secure_val(test):
        return test

def validate_verify(password, verify):
    return password == verify

def make_salt():
    """salt for hashing password"""
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    """hash password using sha256"""
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    """deciphers password and returns True if valid"""
    salt = h.split(',')[1]
    return h == make_pw_hash(name, pw, salt)


def validate(username, password, verify, email):
    response = dict()

    if not validate_name(username):
        response['username_error'] = "The username is not valid."

    if not validate_password(password):
        response['password_error'] = "The password is not valid."

    if not validate_verify(password, verify):
        response['verify_error'] = "The passwords do not match."

    if not validate_email(email):
        response['email_error'] = "The email is not valid."

    return response
