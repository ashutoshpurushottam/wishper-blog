from main import BaseHandler

class UnauthorizedAccessHandler(BaseHandler):
	"""Show unauthorize page with message"""
	def get(self):
		error = self.request.get("error")
		self.render("unauthorized.html", error=error)
