#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.api import users, images
from google.appengine.ext import blobstore, db
from google.appengine.ext.webapp.blobstore_handlers \
    import BlobstoreUploadHandler
import webapp2
from datetime import datetime

from common import (render_page, Comic, get_latest_published_nr,
                    set_latest_published_nr, publish_one_more, _get_comic,
                    get_published_comics)


class ManagePage(BlobstoreUploadHandler):
    def get(self):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)

        comics = Comic.all().order('-nr')
        publish_dates = [date.strftime('%c') for date in find_publish_dates()]
        logout_url = users.create_logout_url('/')
        upload_url = blobstore.create_upload_url('/manage')
        system_time = datetime.now().strftime('%c')

        template_vars = {
            'comics': comics,
            'publish_dates': publish_dates,
            'latest_published_nr': get_latest_published_nr(),
            'logout_url': logout_url,
            'system_time': system_time,
            'upload_url': upload_url,
        }
        render_page(self, 'manage.html', template_vars)

    def post(self):
        if not users.is_current_user_admin():  # Double check
            return self.error(401)

        action = self.request.POST.get('action')
        if action not in ('add', 'remove', 'change_latest', 'publish_one_more',
                          'publish', 'rename', 'change_image',
                          'change_comment', 'change_title_margin',
                          'change_rss_comment', 'change_thumbnail'):
            return self.error(403)
        try:
            getattr(self, action)()
            self.redirect('/manage')
        except Exception as exception:
            self.error(405)
            self.response.out.write('Whoopsiedaisy! ' + str(exception))

    def add(self):
        title = self.param('title')
        image_blobinfo = self.get_upload('image')
        comment = self.param('comment')
        title_margin = self.param('title_margin', int)
        rss_comment = self.param('rss_comment')
        thumbnail_blobinfo = self.get_upload('thumbnail', required=False)

        latest = Comic.all().order('-nr').get()
        nr = latest.nr + 1 if latest else 1
        width, height, image_blob = handle_image(image_blobinfo)

        Comic(nr=nr, title=title, image=image_blob, width=width, height=height,
              comment=comment, title_margin=title_margin,
              rss_comment=rss_comment, thumbnail=thumbnail_blobinfo).put()

    def remove(self):
        to_del = Comic.all().order('-nr').get()
        if to_del is None:
            raise ValueError
        to_del.delete()

    def change_latest(self):
        nr = self.param('nr', int)

        set_latest_published_nr(nr)

    def publish_one_more(self):
        publish_one_more()

    def publish(self):
        nr = self.param('nr', int)

        set_latest_published_nr(nr)

    def rename(self):
        nr = self.param('nr', int)
        name = self.param('name')

        comic = _get_comic(nr)
        comic.title = name
        comic.put()

    def change_image(self):
        image_blobinfo = self.get_upload('image')
        nr = self.param('nr', int)

        comic = _get_comic(nr)
        width, height, blob = handle_image(image_blobinfo)
        comic.width = width
        comic.height = height
        comic.image = blob
        comic.put()

    def change_comment(self):
        nr = self.param('nr', int)
        comment = self.param('comment')

        comic = _get_comic(nr)
        comic.comment = comment
        comic.put()

    def change_title_margin(self):
        nr = self.param('nr', int)
        title_margin = self.param('title_margin', int)

        comic = _get_comic(nr)
        comic.title_margin = title_margin
        comic.put()

    def change_rss_comment(self):
        nr = self.param('nr', int)
        rss_comment = self.param('rss_comment')

        comic = _get_comic(nr)
        comic.rss_comment = rss_comment
        comic.put()

    def change_thumbnail(self):
        thumbnail_blobinfo = self.get_upload('thumbnail')
        nr = self.param('nr', int)

        comic = _get_comic(nr)
        comic.thumbnail = thumbnail_blobinfo
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

    def get_upload(self, name, required=True):
        uploads = self.get_uploads(name)
        if uploads:
            return uploads[0]
        elif required:
            raise ValueError(name + ' werd niet geüpload. Heb je een bestand '
                             'geselecteerd?')
        else:
            return None


class PublishNewComicJob(webapp2.RequestHandler):
    def get(self):
        publish_one_more()


def handle_image(blob_info):
    image = images.Image(blob_key=blob_info)
    image.resize(width=800)
    image_data = image.execute_transforms(quality=100)
    blob_info.delete()
    return image.width, image.height, db.Blob(image_data)


def find_publish_dates():
    """Makes a list of publish dates of all comics.

    This is done by combining the publish dates of already published comics
    (which is saved as an attribute) and calculating the coming publish dates
    by parsing the publish schedule in cron.yaml.
    """
    comics = Comic.all().order('-nr')

    if comics.count() == 0:
        return []

    latest_uploaded_comic = comics.get().nr
    amount_to_publish = latest_uploaded_comic - get_latest_published_nr()
    schedule_str = _find_publish_schedule_string()
    publish_dates = _find_next_publish_dates(schedule_str, amount_to_publish)

    publish_dates += [comic.pub_date for comic in get_published_comics()]

    return publish_dates


def _find_publish_schedule_string():
    import os.path
    import yaml

    with open(os.path.realpath(os.path.join('cron.yaml'))) as cron_file:
        cron_doc = yaml.load(cron_file)['cron']
        return [job['schedule'] for job in cron_doc
                if job['description'] == 'Publish new comic'][0]


def _find_next_publish_dates(schedule_str, n):
    from google.appengine.cron import groctimespecification

    specification = groctimespecification.GrocTimeSpecification(schedule_str)
    next_dates = specification.GetMatches(datetime.now(), n)
    next_dates.reverse()
    return next_dates
