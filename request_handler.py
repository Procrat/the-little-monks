#!/usr/bin/python
# -*- coding: utf-8 -*-
import webapp2

import home, admin, other, login, monks


pages = [('0', other.ZeroEasterPage),
         ('([0-9]*)', home.MainPage),
         ('comic/(.*)', other.ImageHandler),
         ('about', other.AboutPage),
         ('about_monks', monks.AboutMonksPage),
         ('manage', admin.ManagePage),
         ('manage_monks', monks.ManageMonksPage),
         ('_ah/login_required\?continue=(.*)', login.LoginPage),
#         ('rss', rss.RSSPage),
         ('.*', other.NotFoundPage)]

app = webapp2.WSGIApplication([('/' + x, y) for (x, y) in pages], debug=True)
