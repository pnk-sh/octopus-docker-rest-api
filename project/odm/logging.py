from bson.json_util import default
from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import DateTimeField, EmbeddedDocumentField, ListField, SequenceField, StringField

LOG_LEVEL = ('debug', 'info', 'warn', 'error')

class LoggingData(EmbeddedDocument):
    summary = StringField(required=True)
    description = StringField()
    created_at = DateTimeField(required=True)
    
class Logging(Document):
    number = SequenceField()
    
    cluster_id = StringField(required=True)
    binds = ListField(StringField(), required=True)

    data = EmbeddedDocumentField(LoggingData)
    lavel = StringField(chose=LOG_LEVEL, default='debug')

    created_at = DateTimeField()
    deleted_at = DateTimeField()
    
    meta = {
        'auto_create_index': True,
        'index_background': True,
        'indexes': [{
            'fields': ['binds', 'cluster_id']
        }]
    }