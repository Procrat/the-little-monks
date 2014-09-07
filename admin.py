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
        self.show_page()

    def post(self):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)
        action = self.request.POST.get('action')
        if action not in ('add', 'remove', 'rename', 'change_image',
                          'change_comment', 'change_title_margin'):
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
        title_margin = int(POST.get('title_margin'))
        if title is None or not uploads or comment is None or title_margin < 0:
            raise ValueError
        latest = Comic.all().order('-nr').get()
        nr = latest.nr + 1 if latest else 1
        (width, height, blob) = handle_image(uploads[0])
        Comic(nr=nr, title=title, image=blob, width=width, height=height,
              comment=comment, title_margin=title_margin).put()

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
        if comic is None or not uploads:
            raise ValueError
        (width, height, blob) = handle_image(uploads[0])
        comic.width = width
        comic.height = height
        comic.image = blob
        comic.put()

    def change_comment(self, POST):
        nr = POST.get('nr')
        comment = POST.get('comment')
        comic = Comic.all().filter('nr =', int(nr)).get()
        if comic is None or comment is None:
            raise ValueError
        comic.comment = comment
        comic.put()

    def change_title_margin(self, POST):
        nr = int(POST.get('nr'))
        title_margin = int(POST.get('title_margin'))
        comic = Comic.all().filter('nr =', nr).get()
        if comic is None or title_margin < 0:
            raise ValueError
        comic.title_margin = title_margin
        comic.put()


def handle_image(blob_info):
    image = images.Image(blob_key=blob_info)
    image.resize(width=800)
    image_data = image.execute_transforms(quality=100)
    blob_info.delete()
    return (image.width, image.height, db.Blob(image_data))
