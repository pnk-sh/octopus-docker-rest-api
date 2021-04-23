import os
import logging
from werkzeug.wrappers import Request, Response
from mongoengine import connect

def db_connect():
    connect(host=os.getenv('MONGO_URI'))

class DBConnect:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            db_connect()
            logging.info('Connection to mongo success')
            return self.app(environ, start_response)

        except Exception as e:
            logging.info('Connection to mongo failed')
            logging.info('Connection error:', e)

            res = Response(u'Connection to mongo failed', mimetype='text/plain', status=501)
            return res(environ, start_response)