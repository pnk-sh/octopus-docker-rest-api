import os
import logging
import docker
from flask import Response, request
from bson.json_util import dumps, loads

class DockerController:
    @staticmethod
    def getInfo():
        client = docker.DockerClient(base_url=os.getenv('DOCKER_DEAMON_BASE_URI'))

        return Response(dumps({
            'status': 'Success',
            'resualt': client.info()
        }), mimetype='text/json'), 200