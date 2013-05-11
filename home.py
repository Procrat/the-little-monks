#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib

import webapp2

from common import Comic, render_page, loc


class MainPage(webapp2.RequestHandler):
    def get(self, nr):
        latest_comic = Comic.all().order('-nr').get()
        if not latest_comic:
            return self.response.out.write('Upload first comic plz. kthxbai.')
        latest_nr = latest_comic.nr
        nr = int(nr) if nr else latest_nr
        if nr > latest_nr:
            return self.redirect('/%d' % latest_nr)
        comic = Comic.all().filter('nr =', nr).get()
        url = loc + str(nr)
        dic = {'comic_nr': nr,
               'latest': latest_nr,
               'title': comic.title,
               'comment': comic.comment,
               'url': url,
               'comic_width': comic.width,
               'comic_height': comic.height,
               'share_url': urllib.quote(url, ''),
               'share_title': urllib.quote('The Little Monks')}
        render_page(self, 'home.html', dic)
