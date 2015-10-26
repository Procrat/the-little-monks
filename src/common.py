#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
from datetime import datetime, tzinfo, timedelta

import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db, blobstore


if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    LOC_ = 'http://localhost:8080'
else:
    LOC_ = 'http://thelittlemonks.com'
LOC = LOC_ + '/'

ROOT = os.path.join(os.path.dirname(__file__), '..')
JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ROOT),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENV.globals.update(zip=zip)


class Comic(db.Model):
    nr = db.IntegerProperty(required=True)
    title = db.StringProperty(required=True)
    image = db.BlobProperty(required=True)
    width = db.IntegerProperty(required=True)
    height = db.IntegerProperty(required=True)
    title_margin = db.IntegerProperty(required=True, default=0)
    comment = db.TextProperty(required=True)
    thumbnail = blobstore.BlobReferenceProperty()
    rss_comment = db.TextProperty(required=True,
                                  default='New little comic update! Hooray!')
    pub_date = db.DateTimeProperty()

    @property
    def thumbnail_url(self):
        return '{}thumb/{}'.format(LOC, self.nr)


class LatestPublishedComic(db.Model):
    nr = db.IntegerProperty(required=True)


def get_latest_published_nr():
    nr = memcache.get('latest_published_nr')
    if nr is None:
        nr = LatestPublishedComic.all().get().nr
        memcache.add('latest_published_nr', nr, 12 * 60 * 60)
    return nr


def set_latest_published_nr(new_nr):
    latest_comic = LatestPublishedComic.all().get()
    if new_nr != latest_comic.nr:
        # Publish all comics between the previous latest and the new latest
        for nr in range(latest_comic.nr + 1, new_nr + 1):
            new_comic = _get_comic(nr)
            new_comic.pub_date = datetime.now()
            new_comic.save()

        latest_comic.nr = new_nr
        latest_comic.save()
        memcache.set('latest_published_nr', new_nr, 12 * 60 * 60)


def ensure_latest_published_exists():
    latest = LatestPublishedComic.all().get()
    if latest is None:
        latest_comic = Comic.all().order('-nr').get()
        nr = latest_comic.nr if latest_comic is not None else 0
        LatestPublishedComic(nr=nr).put()
        memcache.set('latest_published_nr', nr, 12 * 60 * 60)

ensure_latest_published_exists()


class BrusselsTZ(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=1)

    def dst(self, dt):
        return timedelta(hours=1)

    def tzname(self, dt):
        return "Europe/Brussels"


def _get_comic(nr):
    return Comic.all().filter('nr =', nr).get()


def get_published_comic(nr):
    if nr > get_latest_published_nr():
        return None
    return _get_comic(nr)


def get_published_comics():
    return Comic.all().filter('nr <=', get_latest_published_nr()).order('-nr')


def publish_one_more():
    latest_comic = Comic.all().order('-nr').get()
    if latest_comic is None:
        return

    latest_nr = min(get_latest_published_nr(), latest_comic.nr)
    set_latest_published_nr(latest_nr + 1)


def render_page(req_handler, filename, template_dict=None):
    if template_dict is None:
        template_dict = {}
    template_path = os.path.join('pages', filename)
    template = JINJA_ENV.get_template(template_path)
    template_dict['base'] = LOC
    req_handler.response.write(template.render(template_dict))


def not_found(req_handler):
    req_handler.error(404)
    render_page(req_handler, 'notfound.html')


def error(req_handler, msg):
    req_handler.error(405)
    render_page(req_handler, 'error.html', {'error_msg': msg})


def img_tag(url, width, height, alt=''):
    template = '<img src="{}" width="{}" height="{}" alt="{}" />'
    return template.format(url, width, height, alt)


def a_tag(url, text=None):
    if text is None:
        text = url
    return '<a href="{}">{}</a>'.format(url, text)


JINJA_ENV.filters.update(img_tag=img_tag, a_tag=a_tag)
