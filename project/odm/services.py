  
from mongoengine import Document, EmailField, StringField, ListField, BooleanField
from mongoengine.base.fields import ObjectIdField
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentField


class ServiceSpecLabels(EmbeddedDocument):
    webhook_autodeploy = StringField()
    webhook_tag = StringField()
    webhook_identifier = StringField()

class ServiceSpec(EmbeddedDocument):
    Labels = EmbeddedDocumentField(ServiceSpecLabels)

class Services(Document):
    Spec = EmbeddedDocumentField(ServiceSpec)

    meta = {
        "index_background": True,
        'indexes': [{
            'fields': [
                'Spec.Labels.webhook_autodeploy',
                'Spec.Labels.webhook_tag',
                'Spec.Labels.webhook_identifier'
            ]
        }]
    }