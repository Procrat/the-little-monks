#!/usr/bin/python
# -*- coding: utf-8 -*-
import webapp2

# Add source and libraries folder to PYTHONPATH
import sys
sys.path.extend(['src', 'lib'])

import admin
import contact
import home
import other

import common
common.ensure_latest_published_exists()

pages = [('0', other.ZeroEasterPage),
         ('([0-9]*)', home.MainPage),
         ('comic/(.*)', other.ImageHandler),
         ('thumb/(.*)', other.ThumbnailHandler),
         ('about', other.AboutPage),
         ('about_monks', other.AboutMonksPage),
         ('manage', admin.ManagePage),
         ('manage/publish_new_comic', admin.PublishNewComicJob),
         ('manage/comic/(.*)', other.AdminImageHandler),
         ('rss', other.RSSPage),
         ('contact', contact.ContactPage),
         ('istalavond', other.ISTALAVONDPage),
         ('.*', other.NotFoundPage)]

app = webapp2.WSGIApplication([('/' + x, y) for (x, y) in pages], debug=True)
