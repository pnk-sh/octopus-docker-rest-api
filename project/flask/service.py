import os
import logging
from project.models.webhook import update_webhook
from project.flask.webhook import WebhookController
from project.models.logging import insert_logging
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
        webhook_id = json_data.get('webhook_id')

        if image_name is None:
            return Response(dumps({
                'errors': [100]
            }), mimetype='text/json'), 417
    
        image_name_slice = image_name.split(':')
        if len(image_name_slice) > 1:
            image_name = image_name_slice[0]

        image = client.images.pull(repository=image_name, tag=image_tag)

        service = client.services.get(service_id=service_id)
        resp = service.update(image=f'{image_name}:{image_tag}')
        
        if (resp['Warnings'] is None):
            service = client.services.get(service_id=service_id)
            logging_level = 'info'
            logging_event = 'success'

            if service.force_update():
                update_webhook(webhook_id=webhook_id, body={
                    'service_update_processed': 1
                })
            else:
                logging_level = 'error'
                logging_event = 'failed'
                update_webhook(webhook_id=webhook_id, body={
                    'service_update_failed': 1
                })

            insert_logging(
                summary='Service deployed success',
                description=f'Service-id: {service_id} is now {logging_event} deployed with image {image_name}:{image_tag}',
                level=logging_level,
                binds=[
                    f'service_id-{service_id}',
                    f'webhook_id-{webhook_id}',
                    f'image_name-{image_name}',
                    f'image_tag-{image_tag}',
                ],
            )

            return Response(dumps({
                'service_id': service_id
            }), mimetype='text/json'), 200

        else:
            return Response(dumps({
                'warnings': resp
            }), mimetype='text/json'), 401

    @staticmethod
    def getAll():
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