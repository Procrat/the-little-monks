#!/usr/bin/python
# -*- coding: utf-8 -*-

from webapp2 import RequestHandler
from common import render_page, not_found, Comic


class AboutPage(RequestHandler):
    def get(self):
        render_page(self, 'about.html')


class RSSPage(RequestHandler):
    def get(self):
        self.response.content_type = 'application/rss+xml'
        render_page(self, 'rss.xml', {'comics': list(Comic.all())})


class ContactPage(RequestHandler):
    def get(self):
        render_page(self, 'contact.html')


class NotFoundPage(RequestHandler):
    def get(self):
        not_found(self)


class ZeroEasterPage(RequestHandler):
    def get(self):
        render_page(self, 'zero.html')


class ImageHandler(RequestHandler):
    def get(self, nr):
        try:
            nr = int(nr)
        except:
            return not_found(self)
        comic = Comic.all().filter('nr =', nr).get()
        if comic is None or comic.image is None:
            return not_found(self)
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(comic.image)
