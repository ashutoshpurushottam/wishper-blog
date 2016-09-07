from main import BaseHandler
from base.helpers import check_secure_val

class WelcomeHandler(BaseHandler):
	"""Handler for the welcome page. Redirect to the signup page if no username found"""
	def get(self):
		username = self.request.cookies.get('user')
		if not username:
			self.redirect('/signup')
		else:
			# render welcome page with username
			self.render("welcome.html", username=check_secure_val(username))
