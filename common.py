#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db


LOC_ = 'http://thelittlemonks.com'
LOC = LOC_ + '/'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Comic(db.Model):
    nr = db.IntegerProperty(required=True)
    title = db.StringProperty(required=True)
    image = db.BlobProperty(required=True)
    width = db.IntegerProperty(required=True)
    height = db.IntegerProperty(required=True)
    title_margin = db.IntegerProperty(required=True, default=0)
    comment = db.TextProperty(required=True)
    rss_comment = db.TextProperty(required=True,
                                  default='New little comic update! Hooray!')
    pub_date = db.DateTimeProperty(auto_now_add=True)


class LatestPublishedComic(db.Model):
    nr = db.IntegerProperty(required=True)


def get_latest_published_nr():
    nr = memcache.get('latest_published_nr')
    if nr is None:
        nr = LatestPublishedComic.all().get().nr
        memcache.add('latest_published_nr', nr, 12 * 60 * 60)
    return nr


def set_latest_published_nr(nr):
    latest_comic = LatestPublishedComic.all().get()
    if nr != latest_comic.nr:
        latest_comic.nr = nr
        latest_comic.save()
        memcache.set('latest_published_nr', nr, 12 * 60 * 60)


def _ensure_latest_published_exists():
    latest = LatestPublishedComic.all().get()
    if latest is None:
        latest_comic = Comic.all().order('-nr').get()
        nr = latest_comic.nr if latest_comic is not None else 0
        LatestPublishedComic(nr=nr).put()

_ensure_latest_published_exists()


def get_comic(nr):
    return Comic.all().filter('nr =', nr).get()


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
    template = JINJA_ENVIRONMENT.get_template(os.path.join('pages', filename))
    template_dict['base'] = LOC
    req_handler.response.write(template.render(template_dict))


def not_found(req_handler):
    req_handler.error(404)
    render_page(req_handler, 'notfound.html')


def error(req_handler, msg):
    req_handler.error(405)
    render_page(req_handler, 'error.html', {'error_msg': msg})
