from main import BaseHandler
from models.blog_post import BlogPost
from models.blog_post import blog_key


class NewPostHandler(BaseHandler):
    """create new post handler"""

    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            # redirect to home page
            self.redirect("/")

        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            # save the post
            blog_post = BlogPost(
                subject=subject,
                content=content,
                author=self.user,
                parent=blog_key())
            blog_post.put()
            self.redirect("/blog/%s" % str(blog_post.key.id()))
        else:
            error_message = "Please enter both title and content for your blog entry."
            self.render(
                "newpost.html",
                subject=subject,
                content=content,
                error_message=error_message)
