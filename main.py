#!/usr/bin/env python
#
# Copyright 2016 Ashutosh Purushottam
# Main file containing handlers for urls used in the blog

import os
import webapp2
import jinja2
import time
from google.appengine.ext import ndb

import helpers
from blog_users import *
from blog import *

# define template directory Jinja environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class BaseHandler(webapp2.RequestHandler):
	"""
	Base Handler class with convenience functions
	for page rendering and setting up cookies
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
		cookie_value = helpers.make_secure_val(val)
		self.response.headers.add_header('Set-Cookie','%s=%s; Path=/' % (name, cookie_value))

	def read_cookie(self, name):
		"""reads cookie and returns its value"""
		cookie_value = self.request.cookies.get(name)
		return cookie_value and helpers.check_secure_val(cookie_value)

	def initialize(self, *a, **kw):
		"""page with signed-in user"""
		webapp2.RequestHandler.initialize(self, *a, **kw)
		username = self.read_cookie('user')
		self.user = User.gql("WHERE username = '%s'" % username).get()


class MainHandler(BaseHandler):
	"""render front page"""
	def get(self):
		self.render("index.html")


class SignupHandler(BaseHandler):
    """
    Handles form validation, checks if the username and/or email id already exists.
    In case form is submitted with proper inputs it redirects user to the welcome
    page and adds user to the db
    """
    def get(self):
        self.render("signup.html")

    def post(self):
		# obtain input values from the form
		input_username = self.request.get('username')
		input_password = self.request.get('password')
		input_verify = self.request.get('verify')
		input_email = self.request.get('email')

		validate_response = helpers.validate(input_username, input_password, input_verify, input_email)
		# if validate_response dictionary is empty, the user input values are valid
		# (except that the username/email may already be taken which need to be tested)
		if validate_response:
			username_error = validate_response.get('username_error', "")
			password_error = validate_response.get('password_error', "")
			verify_error = validate_response.get('verify_error', "")
			email_error = validate_response.get('email_error', "")
			self.render("signup.html",
						username_error=username_error,
						password_error=password_error,
						verify_error=verify_error,
						email_error=email_error,
						input_username=input_username,
						input_email=input_email)
		else:
			store_user_response = store_blog_user(input_username, input_password, input_email)
			if store_user_response:
				self.render("signup.html",
							store_user_error = store_user_response,
							input_username=input_username,
							input_email=input_email)
			# user successfully stored in db
			else:
				user_cookie = helpers.make_secure_val(str(input_username))
				self.response.headers.add_header("Set-Cookie", "user=%s; Path=/" % user_cookie)
				time.sleep(0.1)
				self.redirect('/')


class WelcomeHandler(BaseHandler):
	"""Handler for the welcome page. Redirect to the signup page if no username found"""
	def get(self):
		username = self.request.cookies.get('user')
		if not username:
			self.redirect('/signup')
		else:
			# user_name so that it does not clash with the username provided through BaseHandler
			self.render("welcome.html", username=helpers.check_secure_val(username))


class BlogHandler(BaseHandler):
	"""Render blog front page"""
	def get(self):
		# retrieve posts ordered by time
		posts = BlogPost.gql("ORDER BY created DESC")
		self.render("blogfront.html", posts=posts)

class LoginHandler(BaseHandler):
	"""For handling blog users login"""
	def get(self):
		# If the user is already logged in redirect her to welcome page
		username = self.request.cookies.get('user')
		if username:
			# redirect to home page
			self.redirect('/')
		else:
			self.render("login.html")

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		# check if username and password are not empty
		if (not username) or (not password):
			error_message = "Please make sure that username/password is not empty"
			self.render("login.html", error_message = error_message, username=username)
		else:
			#Query the database to check if this username exists or not
			key = User.gql("WHERE username='%s'" % username)
			user = key.get()
			if not user:
				error_message = "The username does not exists. Please go to signup link and register yourself."
				self.render("login.html", error_message=error_message, username=username)
			else:
				is_password_valid = valid_pw(username, password, user.pwd_hashed)
				if not is_password_valid:
					error_message = "Please check your password"
					self.render("login.html", error_message=error_message, username=username)
				else:
					# add the cookie for the user on successful login
					user_cookie = make_secure_val(str(username))
					self.response.headers.add_header("Set-Cookie", "user=%s; Path=/" % user_cookie)
					self.redirect("/")

class LogoutHandler(BaseHandler):
	"""Let user logout by clearing cookie"""
	def get(self):
		username = self.request.cookies.get('user')
		if username:
			self.response.headers.add_header('Set-Cookie', 'user=; Path=/;')
		self.redirect('/')


class NewPostHandler(BaseHandler):
	"""create new post handler"""
	def get(self):
		if self.user:
			self.render("newpost.html")
		else:
			self.redirect('/login')

	def post(self):
		if not self.user:
			# redirect to home page
			self.readirect("/")

		subject = self.request.get('subject')
		content = self.request.get('content')
		if subject and content:
			# save the post
			blog_post = BlogPost(subject=subject, content=content, author=self.user, parent=blog_key())
			blog_post.put()
			self.redirect("/blog/%s" % str(blog_post.key.id()))
		else:
			error_message = "Please enter both title and content for your blog entry."
			self.render("newpost.html", subject=subject, content=content, error_message=error_message)

class EditPostHandler(BaseHandler):
	"""Edit post if authored by user"""
	def get(self):
		if self.user:
			# retrive post
			post_id = self.request.get("post")
			key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
			post = key.get()
			if not post:
				self.error(404)
				return
			else:
				self.render("editpost.html", post=post)
		else:
			# redirected to login page
			self.render('/login')

	def post(self):
		post_id = self.request.get("post")
		key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
		post = key.get()
		# check if user is authorised to edit it
		if post and post.author.username == self.user.username:
			subject = self.request.get("subject")
			content = self.request.get("content")
			if subject and content:
				post.subject = subject
				post.content = content
				post.put()
				time.sleep(0.1)
				self.redirect("/blog")
			else:
				error = "Subject or Content of a blog can't be empty"
				self.render("editpost.html", post=post, error=error)
		else:
			self.redirect("/blog")

class DeletePostHandler(BaseHandler):
	"""Delete post if authored by user"""
	def get(self):
		if self.user:
			post_id = self.request.get("post")
			key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
			post = key.get()
			if not post:
				self.error(404)
				return
			else:
				self.render("deletepost.html", post=post)
		else:
			self.render('/login')

	def post(self):
		post_id = self.request.get("post")
		key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
		post = key.get()
		if post and post.author.username == self.user.username:
			key.delete()
			time.sleep(0.1)
		self.redirect("/blog")

class CommentEditHandler(BaseHandler):
	"""Edit comment handler"""
	def get(self):
		if self.user:
			comment_id = self.request.get("comment")
			key = ndb.Key('Comment', int(comment_id))
			comment = key.get()
			if not comment:
				self.error(404)
				return
			self.render("editcomment.html", content=comment.content, post_id=comment.post_id)
		else:
			self.redirect("/login")

	def post(self):
		# retrieve comment
		comment_id = self.request.get("comment")
		key = ndb.Key('Comment', int(comment_id))
		comment = key.get()
		if comment and comment.author.username == self.user.username:
			content = self.request.get("content")
			if content:
				# save edited comment
				comment.content = content
				comment.put()
				time.sleep(0.1)
				self.redirect("/blog/%s" % comment.post_id)
			else:
				error = "Please do not post empty comment"
				self.render("editcomment.html", content=content, post_id=comment.post_id, error=error)
		else:
			self.redirect("/blog/%s" % comment.post_id)

class DeleteCommentHandler(BaseHandler):
    """Handles deletion of comments"""
    def get(self):
        if self.user:
			# retrieve comment
            comment_id = self.request.get("comment")
            key = ndb.Key('Comment', int(comment_id))
            comment = key.get()
            if not comment:
                self.error(404)
                return
            self.render("deletecomment.html", comment = comment)
        else:
            self.redirect("/login")

    def post(self):
        comment_id = self.request.get("comment")
        key = ndb.Key('Comment', int(comment_id))
        comment = key.get()
        if comment and comment.author.username == self.user.username:
            post_id = comment.post_id
            key.delete()
            time.sleep(0.1)
        self.redirect("/blog/%s" % post_id)




class PostHandler(BaseHandler):
	"""handles single post along with likes and comments"""
	def get(self, post_id):
		post_key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
		post = post_key.get()
		# retrieve comments
		comments = Comment.gql("WHERE post_id = %s ORDER BY created DESC" % int(post_id))
		liked_by_user = None
		if self.user:
			liked_by_user = Like.gql("WHERE post_id = :1 AND author.username = :2", int(post_id), self.user.username).get()
		if not post:
			self.error(404)
			return
		self.render("blogpost.html", post=post, comments=comments, liked_by_user=liked_by_user)

	def post(self, post_id):
		# retrive post from key
		key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
		post = key.get()
		# case: user liking the post
		if self.request.get('like'):
			if post and self.user:
				post.likes += 1
				like = Like(post_id=int(post_id), author=self.user)
				# save like and post
				like.put()
				post.put()
				time.sleep(0.1)
			self.redirect("/blog/%s" % post_id)
		# case: user unliking the post
		elif self.request.get('unlike'):
			if post and self.user:
				post.likes -= 1
				# delete like from db
				like = Like.gql("WHERE post_id = :1 AND author.username = :2", int(post_id), self.user.username).get()
				key = like.key
				key.delete()
				post.put()
				time.sleep(0.1)
			self.redirect("/blog/%s" % post_id)
		# user posted comment on the post
		else:
			content = self.request.get('content')
			if content:
				content = content.encode('ascii', 'ignore')
				comment = Comment(content=str(content), author=self.user, post_id=int(post_id))
				comment.put()
				time.sleep(0.1)
				self.redirect("/blog/%s" % post_id)
			else:
				comments = Comment.gql("WHERE post_id = %s ORDER BY created DESC" % int(post_id))
				self.render("blogpost.html", post=post, comments = comments)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
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
