#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext.webapp import blobstore_handlers
from webapp2 import RequestHandler

from common import render_page, not_found, Comic


class AboutPage(RequestHandler):
    def get(self):
        render_page(self, 'about.html')

class ContactPage(RequestHandler):
    def get(self):
        render_page(self, 'contact.html')

class NotFoundPage(RequestHandler):
    def get(self):
        not_found(self)

class ZeroEasterPage(RequestHandler):
    def get(self):
        render_page(self, 'zero.html')

class ImageHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, nr):
        try:
            nr = int(nr)
        except:
            return not_found(self)
        comic = Comic.all().filter('nr =', nr).get()
        if comic is None or comic.image_info is None:
            return not_found(self)
        self.send_blob(comic.image_info)
