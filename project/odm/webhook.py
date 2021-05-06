from bson.json_util import default
from mongoengine import Document
from mongoengine.fields import DateTimeField, DictField, IntField, SequenceField, StringField

WEBHOOK_STATUS = (
    "pending",
    "processing",
    "completed",
    "error",
    "cancel",
)


class Webhook(Document):
    number = SequenceField()
    status = StringField(choices=WEBHOOK_STATUS, default="pending")
    identifier = StringField()
    webhook = DictField()

    service_update_pending = IntField(default=0)
    service_update_processed = IntField(default=0)
    service_update_failed = IntField(default=0)

    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {"indexes": [{"fields": ["identifier"]}, {"fields": ["status"]}]}
