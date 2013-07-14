#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import blobstore, db
from webapp2 import RequestHandler

from common import render_page


class AboutMonksPage(RequestHandler):
    def get(self):
        render_page(self, 'about_monks.html')
