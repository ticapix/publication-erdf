#!/usr/bin/env python3
import os
import smtplib, email
import requests
from ConfigParser import ConfigParser
import time
import unittest
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import mimetypes

from postbin import PostBin

def pretty(obj):
    return json.dumps(obj, indent=4, sort_keys=True)

class BaseTest(unittest.TestCase):
    @classmethod
    def readConfig(cls):
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '..', 'defaults.cfg'))
        return dict(config.items('MAILGUN'))

    @classmethod
    def createRoute(cls, target_email):
        return requests.post(os.path.join(cls.config['api_url'], 'routes'),
            auth=('api', cls.config['api_key']),
            data={"priority": 0,
                  "description": "test route",
                  "expression": "match_recipient('{email}')".format(email=target_email),
                  "action": ["store(notify='{url}')".format(url=cls.postbin.url), 'stop()']
                  }).json()

    @classmethod
    def deleteRoute(cls):
        return requests.delete(os.path.join(cls.config['api_url'], 'routes', cls.route['route']['id']),
            auth=('api', cls.config['api_key']))

    @classmethod
    def sendMessage(cls, message):
        smtp = smtplib.SMTP(cls.config['smtp_server'])
        smtp.login(cls.config['smtp_username'], cls.config['smtp_password'])
        # smtp.send_message(message) # if py3
        # smtp.set_debuglevel(1)
        smtp.sendmail(message['From'], message['To'], message.as_string())
        smtp.quit()

    @classmethod
    def setUpClass(cls):
        cls.config = cls.readConfig()
        print('read config', cls.config)
        cls.postbin = PostBin().create()
        print('new postbin created', cls.postbin.url)
        cls.route = cls.createRoute('bnpr-pub(\+.*)?@{domain}'.format(domain=cls.config['domain']))
        print('new route created', cls.route)

    @classmethod
    def tearDownClass(cls):
        print('deleting route')
        cls.deleteRoute()
        print('deleting postbin url')
        cls.postbin.delete()


class ForwardEmailAndStoreTest(BaseTest):
    def forwardAndRetrieve(self, content_path, email_to):
        message = email.message_from_file(open(os.path.join(os.path.dirname(__file__), content_path), 'r'))
        message.replace_header("From", 'noreply@noreply.com')
        message.replace_header("To", email_to)
        self.sendMessage(message)
        for i in range(3):
            res = self.postbin.retrieveOne()
            if res:
                return res
            time.sleep(1)
        return None

    @unittest.skip
    def test_no_arg(self):
        res = self.forwardAndRetrieve('email erdf 01 les forges.txt',
            'bnpr-pub@{domain}'.format(domain=self.config['domain']))
        self.assertIsNotNone(res)
        print(res['id'], pretty(json.loads(res['params'])))

    # @unittest.skip
    def test_one_arg(self):
        res = self.forwardAndRetrieve('email erdf 01 les forges.txt',
            'bnpr-pub+cap=400@{domain}'.format(domain=self.config['domain']))
        self.assertIsNotNone(res)
        print(res['id'])
        print pretty(json.loads(res['params']))

    @unittest.skip
    def test_many_args(self):
        res = self.forwardAndRetrieve('email erdf 02 m2m.txt',
            'bnpr-pub+cap=400|graph=0|csv=0@{domain}'.format(domain=self.config['domain']))
        self.assertIsNotNone(res)
        print(res['id'], pretty(json.loads(res['params'])))

class SendEmailAndStoreTest(BaseTest):
    def createMessage(self, filenames, email_body, email_to):
        parts = []
        for filename in filenames:
            filepath = os.path.join(os.path.dirname(__file__), filename)
            mimetype, _ = mimetypes.guess_type(filepath)
            print('adding', filepath, 'with type', mimetype)
            with open(filepath, 'rb') as fd:
                part = MIMEApplication(fd.read(), _subtype = mimetype)
                part.add_header('content-disposition', 'attachment', filename=os.path.basename(filename))
                parts.append(part)

        filepath = os.path.join(os.path.dirname(__file__), email_body)
        print('adding', filepath, 'with encoding', 'iso-8859-1')
        with open(filepath, 'rb') as fd:
            text = MIMEText(fd.read(), _charset='iso-8859-1')
            parts.append(text)

        message = MIMEMultipart(_subparts=parts)
        message['Subject'] = 'Test multipart message'
        message['From'] = 'noreply@noreply.com'
        message['To'] = ', '.join([email_to])
        return message

    def sendAndRetrieve(self, filenames, email_body, email_to):
        message = self.createMessage(filenames, email_body, email_to)
        self.sendMessage(message)
        for i in range(3):
            res = self.postbin.retrieveOne()
            if res:
                return res
            time.sleep(1)
        return None

    @unittest.skip
    def test_no_attachment_no_arg(self):
        res = self.sendAndRetrieve([], 'body 01.txt',
            'bnpr-pub@{domain}'.format(domain=self.config['domain']))
        self.assertIsNotNone(res)
        print(res['id'], pretty(json.loads(res['params'])))

    def test_one_attachment_many_args(self):
        res = self.sendAndRetrieve(['extract01.zip'], 'body 01.txt',
            'bnpr-pub+cap=400|graph=0|csv=0@{domain}'.format(domain=self.config['domain']))
        self.assertIsNotNone(res)
        print(res['id'])
        print pretty(json.loads(res['params']))

    @unittest.skip
    def test_many_attachments_no_arg(self):
        res = self.sendAndRetrieve(['extract01.zip', 'extract02.zip'], 'body 01.txt',
            'bnpr-pub@{domain}'.format(domain=self.config['domain']))
        self.assertIsNotNone(res)
        print(res['id'], pretty(json.loads(res['params'])))

if __name__ == '__main__':
    unittest.main()
