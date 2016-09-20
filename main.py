#!/usr/bin/env python
#
# Copyright 2016 Ashutosh Purushottam
# Main file containing handlers for urls used in the blog

import os
import webapp2
import jinja2
from base.helpers import make_secure_val
from base.helpers import check_secure_val
from models.user import User
# define template directory Jinja environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    """
    Base Handler class with convenience functions
    for page rendering and setting up cookies"
    """

    def write(self, *a, **kw):
        """write to webpage"""
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        """render jinja template"""
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """render template"""
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, val):
        """sets cookie"""
        cookie_value = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' %
            (name, cookie_value))

    def read_cookie(self, name):
        """reads cookie and returns its value"""
        cookie_value = self.request.cookies.get(name)
        return cookie_value and check_secure_val(cookie_value)

    def initialize(self, *a, **kw):
        """page with signed-in user"""
        webapp2.RequestHandler.initialize(self, *a, **kw)
        username = self.read_cookie('user')
        self.user = User.gql("WHERE username = '%s'" % username).get()

from handlers.mainhandler import MainHandler
from handlers.unauthorized import UnauthorizedAccessHandler
from handlers.signup import SignupHandler
from handlers.welcome import WelcomeHandler
from handlers.blog import BlogHandler
from handlers.login import LoginHandler
from handlers.logout import LogoutHandler
from handlers.newpost import NewPostHandler
from handlers.edit_post import EditPostHandler
from handlers.delete_post import DeletePostHandler
from handlers.comment_edit import CommentEditHandler
from handlers.delete_comment import DeleteCommentHandler
from handlers.post import PostHandler


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/unauthorized', UnauthorizedAccessHandler),
    ('/blog', BlogHandler),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/blog/newpost', NewPostHandler),
    ('/blog/([0-9]+)', PostHandler),
    ('/blog/edit', EditPostHandler),
    ('/blog/delete', DeletePostHandler),
    ('/comment/edit', CommentEditHandler),
    ('/comment/delete', DeleteCommentHandler)
], debug=True)
