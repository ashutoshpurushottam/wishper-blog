from main import BaseHandler
from models.user import store_blog_user
from base.helpers import validate
from base.helpers import make_secure_val
import time

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

		validate_response = validate(input_username, input_password, input_verify, input_email)
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
				user_cookie = make_secure_val(str(input_username))
				self.response.headers.add_header("Set-Cookie", "user=%s; Path=/" % user_cookie)
				time.sleep(0.1)
				self.redirect('/')
