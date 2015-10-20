import random
import string
from app import app, db


class Board(db.Model):
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True)
    title = db.Column(db.String(80))
    images = db.relationship('Image', backref='board')
    websites = db.relationship('Website', backref='board')
    colors = db.relationship('Color', backref='board')

    def __init__(self, title='', slug=None):
        self.title = title
        self.slug = slug if slug is not None else self._generate_slug()

    def _generate_slug(self, length=8):
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(length))

    @property
    def static_folder(self):
        return app.config['STATIC_FOLDER_PATH'] + self.path


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    s3_url = db.Column(db.String(160))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    def __init__(self, s3_url):
        self.s3_url = s3_url


class Color(db.Model):
    __tablename__ = 'color'
    id = db.Column(db.Integer, primary_key=True)
    hex_rep = db.Column(db.String(8))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))


class Website(db.Model):
    __tablename__ = 'website'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(160))
    title = db.Column(db.String(80))
    image = db.relationship('Image', backref=db.backref('website',
                                                        uselist=False))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    def __init__(self, url):
        self.url = url
