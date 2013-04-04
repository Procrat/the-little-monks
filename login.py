#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.api import users
from webapp2 import RequestHandler

from common import render_page


PROVIDER_URLS = {'Google': 'https://www.google.com/accounts/o8/id'}


class LoginPage(RequestHandler):
    def get(self, goto):
        providers = {{name: users.create_login_url(goto,
                                                   federated_identity=url)}
                     for name, url in PROVIDER_URLS}
        render_page(self, 'login.html', {'providers': providers})
