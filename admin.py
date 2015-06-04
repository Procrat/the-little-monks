#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.api import users, images
from google.appengine.ext import blobstore, db
from google.appengine.ext.webapp.blobstore_handlers \
    import BlobstoreUploadHandler

from common import render_page, Comic


class ManagePage(BlobstoreUploadHandler):
    def get(self):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)
        comics = Comic.all().order('-nr')
        logout_url = users.create_logout_url('/')
        upload_url = blobstore.create_upload_url('/manage')
        render_page(self, 'manage.html', {'comics': comics,
                                          'logout_url': logout_url,
                                          'upload_url': upload_url})

    def post(self):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)
        action = self.request.POST.get('action')
        if action not in ('add', 'remove', 'rename', 'change_image',
                          'change_comment', 'change_title_margin',
                          'change_rss_comment'):
            return self.error(403)
        try:
            getattr(self, action)()
            self.redirect('/manage')
        except ValueError as error:
            self.error(405)
            self.response.out.write('Whoopsiedaisy! ' + str(error))

    def add(self):
        title = self.param('title')
        uploads = self.get_uploads('image')
        comment = self.param('comment')
        title_margin = self.param('title_margin', int)
        rss_comment = self.param('rss_comment')
        if not uploads:
            raise ValueError('Ik denk dat je geen bestand geselecteerd hebt.')

        latest = Comic.all().order('-nr').get()
        nr = latest.nr + 1 if latest else 1
        (width, height, blob) = handle_image(uploads[0])

        Comic(nr=nr, title=title, image=blob, width=width, height=height,
              comment=comment, title_margin=title_margin,
              rss_comment=rss_comment).put()

    def remove(self):
        to_del = Comic.all().order('-nr').get()
        if to_del is None:
            raise ValueError
        to_del.delete()

    def rename(self):
        nr = self.param('nr', int)
        name = self.param('name')

        comic = Comic.all().filter('nr =', nr).get()
        comic.title = name
        comic.put()

    def change_image(self):
        uploads = self.get_uploads('image')
        nr = self.param('nr', int)

        comic = Comic.all().filter('nr =', nr).get()
        (width, height, blob) = handle_image(uploads[0])
        comic.width = width
        comic.height = height
        comic.image = blob
        comic.put()

    def change_comment(self):
        nr = self.param('nr', int)
        comment = self.param('comment')

        comic = Comic.all().filter('nr =', nr).get()
        comic.comment = comment
        comic.put()

    def change_title_margin(self):
        nr = self.param('nr', int)
        title_margin = self.param('title_margin', int)

        comic = Comic.all().filter('nr =', nr).get()
        comic.title_margin = title_margin
        comic.put()

    def change_rss_comment(self):
        nr = self.param('nr', int)
        rss_comment = self.param('rss_comment')

        comic = Comic.all().filter('nr =', nr).get()
        comic.rss_comment = rss_comment
        comic.put()

    def param(self, name, cast_function=None):
        raw_value = self.request.POST.get(name)
        if not raw_value:
            raise ValueError(name + ' kan niet leeg zijn.')
        if cast_function is None:
            return raw_value
        else:
            try:
                return cast_function(raw_value)
            except ValueError as cast_error:
                raise ValueError(name + ' kon niet omgezet worden (%s)' %
                                 cast_error)


def handle_image(blob_info):
    image = images.Image(blob_key=blob_info)
    image.resize(width=800)
    image_data = image.execute_transforms(quality=100)
    blob_info.delete()
    return (image.width, image.height, db.Blob(image_data))
