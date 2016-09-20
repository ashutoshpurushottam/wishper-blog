from main import BaseHandler
from models.blog_post import blog_key
from google.appengine.ext import ndb
import time


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
                if post.author.username == self.user.username:
                    self.render("editpost.html", post=post)
                else:
                    # redirect to login
                    error_message = "You are not permitted to edit a post that"\
                        " you have not created."
                    self.redirect('/unauthorized?error=' + error_message)
        else:
            # render login page with message that you have been redirected
            error_message = "You can't edit a post without logging in."
            self.redirect('/login?error=' + error_message)

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
