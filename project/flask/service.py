import os
import logging
import docker
from flask import Response, request
from bson.json_util import dumps, loads

from project.odm.services import Services as OdmServices

class DockerServiceController:
    @staticmethod
    def update(service_id: str):
        client = docker.DockerClient(base_url=os.getenv('DOCKER_DEAMON_BASE_URI'))
        client.login(
            username=os.getenv('DOCKER_REGISTRY_USERNAME'),
            password=os.getenv('DOCKER_REGISTRY_PASSWORD'),
        )
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

    @staticmethod
    def get_all():
        service_filter = {}

        if (request.args.get('autodeploy')):
            service_filter['Spec.Labels.webhook_autodeploy'] = request.args.get('autodeploy')

        if (request.args.get('tag')):
            service_filter['Spec.Labels.webhook_tag'] = request.args.get('tag')

        if (request.args.get('identifier')):
            service_filter['Spec.Labels.webhook_identifier'] = request.args.get('identifier')

        row = OdmServices.objects.aggregate([{
            '$match': service_filter
        }, {
            '$project': {
                '_id': 0,
                'ID': 1,
                'ClusterID': 1,
                'Name': '$Spec.Name',
                'Image': '$Spec.TaskTemplate.ContainerSpec.Image'
            }
        }])

        return Response(dumps({
            'services': row
        }), mimetype='text/json'), 200