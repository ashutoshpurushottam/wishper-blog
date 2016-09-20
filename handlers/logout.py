from main import BaseHandler


class LogoutHandler(BaseHandler):
    """Let user logout by clearing cookie"""

    def get(self):
        username = self.request.cookies.get('user')
        if username:
            self.response.headers.add_header('Set-Cookie', 'user=; Path=/;')
        self.redirect('/')
