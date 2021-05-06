from datetime import datetime
from project.models.logging import insert_logging
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
                logging_binds = [
                    f'webook_id-{str(webhook[0].pk)}',
                    f'webook_number-{webhook[0].number}',
                    f'webook_identifier-{webhook[0].identifier}',
                ]
                logging_level = 'info'
                logging_description = []
                
                fields_to_update = {
                    'updated_at': datetime.utcnow()
                }

                if data.get('service_update_pending') and webhook[0].service_update_pending != int(data.get('service_update_pending')):
                    before_service_update_pending_count = webhook[0].service_update_pending
                    service_update_pending_count = int(data.get('service_update_pending'))

                    fields_to_update['service_update_pending'] = int(data.get('service_update_pending'))
                    logging_description.append(f'Service update pending {before_service_update_pending_count} → {service_update_pending_count}')

                if data.get('service_update_processed'):
                    before_service_update_processed_count = webhook[0].service_update_processed
                    service_update_processed_count = webhook[0].service_update_processed + int(data.get('service_update_processed'))

                    fields_to_update['service_update_processed'] = service_update_processed_count
                    logging_description.append(f'Service update processed {before_service_update_processed_count} → {service_update_processed_count}')

                if data.get('service_update_failed'):
                    before_service_update_failed_count = webhook[0].service_update_failed
                    service_update_failed_count = webhook[0].service_update_failed + int(data.get('service_update_failed'))

                    fields_to_update['service_update_failed'] = service_update_failed_count
                    logging_description.append(f'Service update failed {before_service_update_failed_count} → {service_update_failed_count}')

                if data.get('status') and webhook[0].status != data.get('status'):
                    before_webhook_status = webhook[0].status
                    webhook_status = data.get('status')

                    fields_to_update['status'] = webhook_status
                    logging_description.append(f'status {before_webhook_status} → {webhook_status}')

                webhook.update(**fields_to_update)

                if not data.get('status') and webhook[0].service_update_pending <= (webhook[0].service_update_processed + webhook[0].service_update_failed):
                    before_webhook_status = webhook[0].status
                    webhook_status = 'completed'
                    
                    if webhook[0].service_update_failed > 0:
                        webhook_status = 'error'
                        logging_level = 'warn'
                    elif webhook[0].service_update_pending < (webhook[0].service_update_processed + webhook[0].service_update_failed):
                        webhook_status = 'error'
                        logging_level = 'warn'

                    webhook.update(**{
                        'status': webhook_status
                    })

                    logging_description.append(f'status {before_webhook_status} → {webhook_status}')

                insert_logging(
                    summary='Webhook - updated',
                    description="\n".join(logging_description),
                    binds=logging_binds,
                    level=logging_level
                )
                
                return Response(dumps({
                }), mimetype='text/json'), 200
            else:
                return Response(dumps({
                }), mimetype='text/json'), 404

        else:
            return Response(dumps({
            }), mimetype='text/json'), 204
