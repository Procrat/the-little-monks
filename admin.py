#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp.blobstore_handlers import BlobstoreUploadHandler

from common import render_page, Comic


class ManagePage(BlobstoreUploadHandler):
    def get(self):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)
        self.show_page()

    def post(self):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)
        action = self.request.POST.get('action')
        if action not in ('add', 'remove', 'rename', 'change_image',
                          'change_comment'):
            return self.error(403)
        try:
            getattr(self, action)(self.request.POST)
            self.show_page()
        except ValueError:
            self.error(405)
            self.response.out.write('That doesn\'t seem right to me, liefje!')

    def show_page(self):
        comics = [(comic.nr, comic.title, comic.comment)
                  for comic in Comic.all().order('nr')]
        logout_url = users.create_logout_url('/')
        upload_url = blobstore.create_upload_url('/manage')
        render_page(self, 'manage.html', {'comics': comics,
                                          'logout_url': logout_url,
                                          'upload_url': upload_url})

    def add(self, POST):
        title = POST.get('title')
        uploads = self.get_uploads('image')
        comment = POST.get('comment')
        if title is None or not uploads or comment is None:
            raise ValueError
        latest = Comic.all().order('-nr').get()
        nr = latest.nr + 1 if latest else 1
        Comic(nr=nr, title=title, image_info=uploads[0].key(),
                comment=comment).put()

    def remove(self, POST):
        to_del = Comic.all().order('-nr').get()
        if to_del is None:
            raise ValueError
        to_del.delete()

    def rename(self, POST):
        nr = POST.get('nr')
        name = POST.get('name')
        comic = Comic.all().filter('nr =', int(nr)).get()
        if comic is None or name is None:
            raise ValueError
        comic.title = name
        comic.put()

    def change_image(self, POST):
        uploads = self.get_uploads('image')
        nr = POST.get('nr')
        comic = Comic.all().filter('nr =', int(nr)).get()
        logging.debug("%s en %s en %s" % (nr, comic, uploads))
        if comic is None or not uploads:
            raise ValueError
        comic.image_info = uploads[0].key()
        comic.put()

    def change_comment(self, POST):
        nr = POST.get('nr')
        comment = POST.get(' comment')
        comic = Comic.all().filter('nr =', int(nr)).get()
        if comic is None or comment is None:
            raise ValueError
        comic.comment = comment
        comic.put()
