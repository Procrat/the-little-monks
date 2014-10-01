#!/usr/bin/python
# -*- coding: utf-8 -*-
import webapp2

import home, admin, other, contact


pages = [('0', other.ZeroEasterPage),
         ('([0-9]*)', home.TemporaryPage),
         ('comic/(.*)', other.ImageHandler),
         ('about', other.AboutPage),
         ('about_monks', other.AboutMonksPage),
         ('manage', admin.ManagePage),
         ('rss', other.RSSPage),
         ('contact', contact.ContactPage),
         ('.*', other.NotFoundPage)]

app = webapp2.WSGIApplication([('/' + x, y) for (x, y) in pages], debug=True)
