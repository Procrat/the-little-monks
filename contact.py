#!/usr/bin/python
# -*- coding: utf-8 -*-
import webapp2
from google.appengine.api import mail

from common import render_page, error


SENDER  = 'TLMMail <mail@thelittlemonks.appspotmail.com>'
TO      = 'Myrjam Van de Vijver <myrjamvdv@gmail.com>'
SUBJECT = '[TLM] %s'
BODY    = '%s <%s> (birthdate: %s) wrote the following:\n\n%s'


class ContactPage(webapp2.RequestHandler):
    def get(self):
        render_page(self, 'contact.html')

    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        birth_day = int(self.request.get('birth[day]'))
        birth_month = int(self.request.get('birth[month]'))
        birth_year = int(self.request.get('birth[year]'))
        subject = self.request.get('subject')
        comment = self.request.get('comment')
        if not all((name, email, subject, comment)):
            return error(self, 'You didn\'t supply everything.')
        if not mail.is_email_valid(email):
            return error(self, 'You entered an incorrect email address.')
        birth_date = '%02d/%02d/%04d' % (birth_day, birth_month, birth_year)
        body = BODY % (name, email, birth_date, comment)
        import logging
        logging.debug(body)
        mail.send_mail(sender=SENDER, to=TO, subject=SUBJECT % subject + body,
                       reply_to=email, body=body)
        render_page(self, 'contact_thanks.html')
