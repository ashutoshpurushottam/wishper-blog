from main import BaseHandler
from google.appengine.ext import ndb
import time

class DeleteCommentHandler(BaseHandler):
	"""Comment deletion handler"""
	def get(self):
		if self.user:
			comment_id = self.request.get("comment")
			key = ndb.Key('Comment', int(comment_id))
			comment = key.get()
			if comment:
				if comment.author.username == self.user.username:
					self.render("deletecomment.html", comment=comment)
				else:
					error_message = "You can't delete a comment posted by other user"
					self.redirect('/unauthorized?error=' + error_message)
			else:
				self.error(404)
				return
		else:
			error_message = "You can't delete a comment without logging in."
			self.redirect('/login?error=' + error_message)

	def post(self):
		comment_id = self.request.get("comment")
		key = ndb.Key('Comment', int(comment_id))
		comment = key.get()
		if comment and comment.author.username == self.user.username:
			post_id = comment.post_id
			key.delete()
			time.sleep(0.1)
		self.redirect("/blog/%s" % post_id)
