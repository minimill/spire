import hmac
import hashlib
import json
from base64 import b64encode
from datetime import datetime, timedelta
from app import app

POLICY_DICT = {
    "expiration": None,
    "conditions": [
        {"bucket": "minimill-spire"},
        ["starts-with", "$key", "uploads/"],
        {"acl": "public-read"},
        ["starts-with", "$Content-Type", ""],
        ["content-length-range", 0, 1000048576]
    ]
}


def new_aws_formdata():

    POLICY_DICT['expiration'] = utc(datetime.utcnow() +
                                    timedelta(seconds=60 * 60))
    policy_document = json.dumps(POLICY_DICT)
    policy = b64encode(policy_document)
    signature = b64encode(hmac.new(app.config['AWS_SECRET_ACCESS_KEY'],
                                   policy,
                                   hashlib.sha1).digest())
    return {
        'policy': policy,
        'signature': signature
    }


def utc(dt):
    return datetime.strftime(dt, '%Y-%m-%dT%H:%M:%SZ')
