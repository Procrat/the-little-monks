#!/usr/bin/python
# -*- coding: utf-8 -*-
import webapp2

# Add source folder to PYTHONPATH
import sys
sys.path.append('src')

import admin
import contact
import home
import other


pages = [('0', other.ZeroEasterPage),
         ('([0-9]*)', home.MainPage),
         ('comic/(.*)', other.ImageHandler),
         ('about', other.AboutPage),
         ('about_monks', other.AboutMonksPage),
         ('manage', admin.ManagePage),
         ('manage/publish_new_comic', admin.PublishNewComicJob),
         ('rss', other.RSSPage),
         ('contact', contact.ContactPage),
         ('.*', other.NotFoundPage)]

app = webapp2.WSGIApplication([('/' + x, y) for (x, y) in pages], debug=True)
