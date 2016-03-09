#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, time

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp.blobstore_handlers import \
    BlobstoreDownloadHandler
from webapp2 import RequestHandler

from common import (BrusselsTZ, _get_comic, get_published_comic,
                    get_published_comics, not_found, render_page)


class AboutPage(RequestHandler):
    def get(self):
        render_page(self, 'about.html')


class AboutMonksPage(RequestHandler):
    def get(self):
        render_page(self, 'about_monks.html')


class RSSPage(RequestHandler):
    def get(self):
        from datetime import datetime
        self.response.content_type = 'application/rss+xml'
        render_page(self, 'rss.xml', {
            'comics': list(get_published_comics()),
            'year': datetime.now().year,
        })


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
    # TODO merge this to blobstore

    def get(self, nr):
        try:
            nr = int(nr)
        except:
            return not_found(self)

        comic = get_published_comic(nr)

        if comic is None or comic.image is None:
            return not_found(self)

        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(comic.image)


class AdminImageHandler(RequestHandler):
    def get(self, nr):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)

        try:
            nr = int(nr)
        except:
            return not_found(self)

        comic = _get_comic(nr)

        if comic is None or comic.image is None:
            return not_found(self)

        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(comic.image)


class ThumbnailHandler(BlobstoreDownloadHandler):
    def get(self, nr):
        try:
            nr = int(nr)
        except:
            return not_found(self)

        if users.is_current_user_admin():
            comic = _get_comic(nr)
        else:
            comic = get_published_comic(nr)

        if (comic is None or
                comic.thumbnail is None or
                not blobstore.get(comic.thumbnail.key())):
            return not_found(self)

        self.response.headers['Content-Type'] = 'image/png'
        self.send_blob(comic.thumbnail)


class ISTALAVONDPage(RequestHandler):
    def get(self):
        now = datetime.now(tz=BrusselsTZ())
        evening = datetime.combine(now, time(17, 30, tzinfo=BrusselsTZ()))
        secs_till_evening = (evening - now).total_seconds()
        template_dict = {'seconds_remaining': int(secs_till_evening)}
        render_page(self, 'istalavond.html', template_dict)
