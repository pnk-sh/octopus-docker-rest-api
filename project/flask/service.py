import os
import logging
import docker
from flask import Response, request
from bson.json_util import dumps, loads

class DockerServiceController:
    @staticmethod
    def update(service_id: str):
        client = docker.DockerClient(base_url=os.getenv('DOCKER_DEAMON_BASE_URI'))
        json_data = request.get_json()

        image_name = json_data.get('image')
        image_tag = json_data.get('tag', 'latest')

        if image_name is None:
            return Response(dumps({
                'errors': [100]
            }), mimetype='text/json'), 417

        image = client.images.pull(repository=image_name, tag=image_tag)

        service = client.services.get(service_id=service_id)
        resp = service.update(image=f'{image_name}:{image_tag}')
        
        if (resp['Warnings'] is None):
            service = client.services.get(service_id=service_id)
            service.force_update()

            return Response(dumps({
                'service_id': service_id
            }), mimetype='text/json'), 200

        else:
            return Response(dumps({
                'warnings': resp
            }), mimetype='text/json'), 401

        