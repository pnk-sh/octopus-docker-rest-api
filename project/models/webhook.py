import os
import requests
from datetime import datetime


def update_webhook(webhook_id: str, body: object):
    try:
        requests.post(f'http://localhost:5000/webhook/{webhook_id}', json=body)
        
    except requests.exceptions.RequestException as e:
        pass