from datetime import datetime
import logging
from flask import Response, request
from bson.json_util import dumps, loads

from project.odm.webhook import Webhook as OdmWebhook

class WebhookController:
    @staticmethod
    def update(webhook_id: str):
        data = request.get_json()

        if len(data) > 0:
            webhook = OdmWebhook.objects(pk=webhook_id)
            if len(webhook) > 0:
                fields_to_update = {
                    'updated_at': datetime.utcnow()
                }

                if data.get('service_update_pending'):
                    fields_to_update['service_update_pending'] = int(data.get('service_update_pending'))

                if data.get('service_update_processed'):
                    fields_to_update['service_update_processed'] = webhook[0].service_update_processed + int(data.get('service_update_processed'))

                if data.get('service_update_failed'):
                    fields_to_update['service_update_failed'] = webhook[0].service_update_failed + int(data.get('service_update_failed'))

                if data.get('status'):
                    fields_to_update['status'] = data.get('status')

                webhook.update(**fields_to_update)

                if webhook[0].service_update_pending <= (webhook[0].service_update_processed + webhook[0].service_update_failed):
                    webhook_status = 'completed'
                    
                    if webhook[0].service_update_failed > 0:
                        webhook_status = 'error'
                    elif webhook[0].service_update_pending < (webhook[0].service_update_processed + webhook[0].service_update_failed):
                        webhook_status = 'error'
                    
                    webhook.update(**{
                        'status': webhook_status
                    })

                return Response(dumps({
                }), mimetype='text/json'), 200
            else:
                return Response(dumps({
                }), mimetype='text/json'), 404

        else:
            return Response(dumps({
            }), mimetype='text/json'), 204
