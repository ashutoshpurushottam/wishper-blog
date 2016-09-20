from main import BaseHandler
from models.blog_post import blog_key
from google.appengine.ext import ndb
import time


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
                if post.author.username == self.user.username:
                    self.render("deletepost.html", post=post)
                else:
                    error_message = "You are not permitted to delete a post"\
                        " that you have not created."
                    self.redirect('/unauthorized?error=%s' % error_message)
        else:
            # render login page with message that you have been redirected
            error_message = "You can't delete a post without logging in."
            self.redirect('/login?error=' + error_message)

    def post(self):
        post_id = self.request.get("post")
        key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
        post = key.get()
        if post and self.user and post.author.username == self.user.username:
            key.delete()
            time.sleep(0.1)
        self.redirect("/blog")
