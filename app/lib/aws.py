import hmac
import hashlib
import json
import boto
from base64 import b64encode
from datetime import datetime, timedelta


class S3(object):

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

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.secret_access_key = app.config["AWS_SECRET_ACCESS_KEY"]
        self.access_key_id = app.config["AWS_ACCESS_KEY_ID"]
        conn = boto.connect_s3(self.access_key_id, self.secret_access_key)
        self.bucket = conn.get_bucket(app.config["S3_BUCKET"])

    def upload_to_s3(self, local_path, filename, content_type):
        # Upload the File
        sml = self.bucket.new_key('uploads/' + filename)
        with open(local_path, 'rb') as local_file:
            sml.set_contents_from_string(local_file.read())

        # Set the file's permissions.
        sml.set_acl('public-read')

    def new_aws_formdata(self):
        self.POLICY_DICT['expiration'] = utc(datetime.utcnow() +
                                             timedelta(seconds=60 * 60))
        policy_document = json.dumps(self.POLICY_DICT)
        policy = b64encode(policy_document)
        signature = b64encode(hmac.new(self.secret_access_key,
                                       policy,
                                       hashlib.sha1).digest())
        return {
            'policy': policy,
            'signature': signature
        }


def iso_timestamp():
    now = datetime.now()
    utc_now = datetime.utcnow()
    delta = now - utc_now
    hh, mm = divmod((delta.days * 24 * 60 * 60 + delta.seconds + 30) // 60, 60)
    return '%s%+02d:%02d' % (now.isoformat(), hh, mm)


def utc(dt):
    return datetime.strftime(dt, '%Y-%m-%dT%H:%M:%SZ')
