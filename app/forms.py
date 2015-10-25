import string
from flask_wtf import Form
from wtforms import StringField
# from wtforms_components import PassiveHiddenField
from wtforms.validators import DataRequired, ValidationError
from app.models import Board

BAD_FOLDER = 'Folder name should only contain numbers, letters, and dashes'
NO_SUCH_SLUG = 'No such slug'
INVALID_HEX = 'Invalid color hex'


def valid_slug(form, field):
    """A validator that ensures that there is a board in the database with the
    slug that is the same as the field's data.
    :param form: The parent form
    :type form: :class:`Form`
    :param field: The field to validate
    :type field: :class:`Field`
    """
    board = Board.query.filter_by(slug=field.data).first()
    if not board:
        raise ValidationError(NO_SUCH_SLUG)


def valid_hex(form, field):
    """A validator that ensures that there is a board in the database with the
    slug that is the same as the field's data.
    :param form: The parent form
    :type form: :class:`Form`
    :param field: The field to validate
    :type field: :class:`Field`
    """
    if (not all(c in string.hexdigits for c in field.data) or
            len(field.data) not in (3, 6)):
        raise ValidationError(INVALID_HEX)


class SpireForm(Form):

    def __init__(self, *args, **kwargs):
        super(SpireForm, self).__init__(prefix=self._prefix, *args, **kwargs)

    @property
    def _prefix(self):
        raise NotImplemented


class EditBoardForm(SpireForm):
    _prefix = 'board-'
    title = StringField('Project Name')
    slug = StringField('project-name', [DataRequired()])


class TextForm(SpireForm):
    _prefix = 'text-'
    slug = StringField('slug', [DataRequired(), valid_slug])
    text = StringField('text', [DataRequired(), valid_hex])


class ImageForm(SpireForm):
    _prefix = 'image-'
    slug = StringField('slug', [DataRequired(), valid_slug])
    filename = StringField('filename', [DataRequired()])


def get_forms(board):
    return {
        'board': EditBoardForm(title=board.title,
                               slug=board.slug),
        'text': TextForm(slug=board.slug),
        'image': ImageForm(slug=board.slug)
    }
