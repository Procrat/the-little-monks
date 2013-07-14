#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

import webapp2
from google.appengine.api import mail

from common import render_page, error


SENDER = 'TLMMail <mail@thelittlemonks.appspotmail.com>'
TO = 'Myrjam Van de Vijver <myrjamvdv@gmail.com>'
SUBJECT = '[TLM] %s'


class ContactPage(webapp2.RequestHandler):
    def get(self):
        render_page(self, 'contact.html')

    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        subject = self.request.get('subject')
        comment = self.request.get('comment')
        if not name or not email or not subject or not comment:
            return error(self, 'You didn\'t supply everything.')
        if not mail.is_email_valid(email):
            return error(self, 'You entered an incorrect email address.')
        mail.send_mail(sender=SENDER, to=TO, subject=SUBJECT % subject,
                       reply_to=email, body=comment)
        render_page(self, 'contact_thanks.html')
