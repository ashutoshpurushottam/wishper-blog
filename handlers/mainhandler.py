from main import BaseHandler

class MainHandler(BaseHandler):
	"""render front page"""
	def get(self):
		self.render("index.html")
