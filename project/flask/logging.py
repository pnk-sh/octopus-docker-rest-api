from logging import log
from datetime import datetime
import logging
from flask import Response, request
from bson.json_util import dumps, loads

from project.odm.logging import Logging as OdmLogging, LoggingData as OdmLoggingData

class LoggingController:
    @staticmethod
    def getAll():
        log_filter = {}
        if (request.args.get('binds')):
            binds = request.args.get('binds')
            
            if isinstance(binds, str):
                binds = binds.split(',')
            
            log_filter['binds'] = {
                '$in': binds
            }

        logs = OdmLogging.objects.aggregate([{
            '$match': log_filter
        }])

        return Response(dumps({
            'content': logs
        }), mimetype='text/json'), 200

    @staticmethod
    def insert():
        data = request.get_json()

        created_at_format = data.get('created_at_format', '%Y-%m-%d %H:%M:%S.%f')

        logging = OdmLogging()
        logging.cluster_id = 'custom-id'
        logging.binds = data.get('binds', [])
        logging.data = OdmLoggingData()
        logging.data.summary = data.get('summary')
        logging.data.description = data.get('description', '')
        logging.data.created_at = datetime.strptime(data.get('created_at'), created_at_format)
        logging.lavel = data.get('level', 'debug')
        logging.created_at = datetime.utcnow()
        logging.save()

        return Response(dumps({
            'id': logging.pk
        }), mimetype='text/json'), 200