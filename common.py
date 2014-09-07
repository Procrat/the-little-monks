#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from google.appengine.ext import db
from google.appengine.ext.webapp import template


loc_ = 'http://thelittlemonks.com'
loc = loc_ + '/'


class Comic(db.Model):
    nr = db.IntegerProperty(required=True)
    title = db.StringProperty(required=True)
    image = db.BlobProperty(required=True)
    width = db.IntegerProperty(required=True)
    height = db.IntegerProperty(required=True)
    title_margin = db.IntegerProperty(required=True, default=0)
    comment = db.TextProperty(required=True)
    pub_date = db.DateTimeProperty(auto_now_add=True)


def render_page(req_handler, filename, template_dict={}):
    path = os.path.join(os.path.dirname(__file__), 'pages', filename)
    template_dict['base'] = loc
    req_handler.response.out.write(template.render(path, template_dict))


def not_found(req_handler):
    req_handler.error(404)
    render_page(req_handler, 'notfound.html')


def error(req_handler, msg):
    req_handler.error(405)
    render_page(req_handler, 'error.html', {'error_msg': msg})
