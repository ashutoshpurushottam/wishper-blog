from main import BaseHandler
from models.blog_post import BlogPost


class BlogHandler(BaseHandler):
    """Render blog front page"""

    def get(self):
        # retrieve posts ordered by time
        posts = BlogPost.gql("ORDER BY created DESC")
        self.render("blogfront.html", posts=posts)
