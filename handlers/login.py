from main import BaseHandler
from models.user import User
from base.helpers import valid_pw
from base.helpers import make_secure_val

class LoginHandler(BaseHandler):
	"""For handling blog users login"""
	def get(self):
		error_message = self.request.get('error')
		self.render("login.html", error_message=error_message)

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
