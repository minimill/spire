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
    text_blocks = db.relationship('TextBlock', backref='board')

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
    filename = db.Column(db.String(160))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    def __init__(self, filename):
        self.filename = filename

    @property
    def url(self):
        return app.config['S3_BASEURL'] + self.filename


class TextBlock(db.Model):
    __tablename__ = 'textblock'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.UnicodeText())
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))


class Color(db.Model):
    __tablename__ = 'color'
    id = db.Column(db.Integer, primary_key=True)
    hex_rep = db.Column(db.String(8))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))

    def __init__(self, hex, *args, **kwargs):
        self.hex_rep = self._valid_hex(hex)
        super(Color, self).__init__(*args, **kwargs)

    @staticmethod
    def is_valid_hex(raw_hex):
        hex = raw_hex.strip().lstrip('#')
        if (not all(c in string.hexdigits for c in hex) or
                len(hex) not in (3, 6)):
            return False
        return True

    def _valid_hex(self, hex):
        hex = hex.lstrip('#')
        if not Color.is_valid_hex(hex):
            raise ValueError('Invalid color hex value')
        if len(hex) == 3:
            hex = ''.join((c + c for c in hex))
        return hex.upper()

    @property
    def hex(self):
        return self.hex_rep

    @hex.setter
    def set_hex(self, hex):
        self.hex_rep = self._valid_hex(hex)


class Website(db.Model):
    __tablename__ = 'website'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(160))
    title = db.Column(db.String(80))
    image = db.relationship('Image', backref=db.backref('website',
                                                        uselist=False))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
