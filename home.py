#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib

import webapp2

from common import Comic, render_page, LOC


class MainPage(webapp2.RequestHandler):
    def get(self, nr):
        # Check if there are any comics
        latest_comic = Comic.all().order('-nr').get()
        if not latest_comic:
            return self.response.out.write('Upload first comic plz. kthxbai.')

        # Redirect to the latest comic if the number exceeds the latest one
        latest_nr = latest_comic.nr
        nr = int(nr) if nr else latest_nr
        if nr > latest_nr:
            return self.redirect('/%d' % latest_nr)

        # Get the corresponding comic
        comic = Comic.all().filter('nr =', nr).get()

        # Fill data dict and render
        dic = {'latest': latest_nr,
               'comic': comic,
               'share_url': urllib.quote(LOC + str(nr), ''),
               'share_title': urllib.quote('The Little Monks')}
        render_page(self, 'home.html', dic)
