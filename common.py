#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import jinja2
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
