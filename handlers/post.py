from main import BaseHandler
from google.appengine.ext import ndb
from models.comment import Comment
from models.like import Like
from models.blog_post import blog_key
import time


class PostHandler(BaseHandler):
    """handles single post along with likes and comments"""

    def get(self, post_id):
        post_key = ndb.Key('BlogPost', int(post_id), parent=blog_key())
        post = post_key.get()
        # retrieve comments
        comments = Comment.gql(
            "WHERE post_id = %s ORDER BY created DESC" %
            int(post_id))
        liked_by_user = None
        if self.user:
            liked_by_user = Like.gql(
                "WHERE post_id = :1 AND author.username = :2",
                int(post_id),
                self.user.username).get()
        if not post:
            self.error(404)
            return
        self.render(
            "blogpost.html",
            post=post,
            comments=comments,
            liked_by_user=liked_by_user)

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
                like = Like.gql(
                    "WHERE post_id = :1 AND author.username = :2",
                    int(post_id),
                    self.user.username).get()
                key = like.key
                key.delete()
                post.put()
                time.sleep(0.1)
            self.redirect("/blog/%s" % post_id)
        # user posted comment on the post
        else:
            content = self.request.get('content')
            if content and self.user:
                content = content.encode('ascii', 'ignore')
                comment = Comment(
                    content=str(content),
                    author=self.user,
                    post_id=int(post_id))
                comment.put()
                time.sleep(0.1)
                self.redirect("/blog/%s" % post_id)
            else:
                comments = Comment.gql(
                    "WHERE post_id = %s ORDER BY created DESC" %
                    int(post_id))
                self.render("blogpost.html", post=post, comments=comments)
