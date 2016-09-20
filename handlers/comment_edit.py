from main import BaseHandler
from google.appengine.ext import ndb
import time


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
            if comment.author.username == self.user.username:
                self.render(
                    "editcomment.html",
                    content=comment.content,
                    post_id=comment.post_id)
            else:
                error_message = "You can not edit comments posted by other users."
                self.redirect('/unauthorized?error=%s' % error_message)
        else:
            # render login page with message that you have been redirected
            error_message = "You can't edit a comment without logging in."
            self.redirect('/login?error=%s' % error_message)

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
                self.render(
                    "editcomment.html",
                    content=content,
                    post_id=comment.post_id,
                    error=error)
        else:
            self.redirect("/blog/%s" % comment.post_id)
