from sys import exit, stderr

try:
    import secrets

    AWS_USER_NAME = secrets.AWS_USER_NAME
    AWS_ACCESS_KEY_ID = secrets.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = secrets.AWS_SECRET_ACCESS_KEY
    SECRET_KEY = secrets.SECRET_KEY
    META_TITLE = 'Spire'
    META_DESCRIPTION = (
        'Spire: a fast and easy inspiration board.'
    )
    META_NAME = 'Spire'
    META_TWITTER_HANDLE = '@minimill_co'
    META_DOMAIN = 'spire.fyi'
    META_URL = 'https://' + META_DOMAIN
    META_IMAGE = 'img/lock.svg'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    S3_BASEURL = 'https://s3.amazonaws.com/minimill-spire/'

except ImportError:
    print >> stderr, 'Could not find config/secrets.py.  Do you have one?'
    exit(1)

except AttributeError as e:
    attr = e.message.lstrip('\'module\' object has no attribute ').rstrip('\'')
    print >> stderr, 'config/secrets.py is missing the key "%s"' % attr
    exit(1)
