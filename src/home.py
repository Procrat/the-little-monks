#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib

import webapp2

from common import render_page, LOC, get_latest_published_nr, get_comic


class MainPage(webapp2.RequestHandler):
    def get(self, nr):
        latest_nr = get_latest_published_nr()

        # Check if there are any comics
        if latest_nr < 1:
            upload_plz = 'Upload/publish first comic plz. kthxbai.'
            return self.response.out.write(upload_plz)

        # Redirect to the latest comic if the number exceeds the latest one
        nr = int(nr) if nr else latest_nr
        if nr > latest_nr:
            return self.redirect('/%d' % latest_nr)

        # Get the corresponding comic
        comic = get_comic(nr)

        # Fill data dict and render
        dic = {'latest': latest_nr,
               'comic': comic,
               'share_url': urllib.quote(LOC + str(nr), ''),
               'share_title': urllib.quote('The Little Monks')}
        render_page(self, 'home.html', dic)
