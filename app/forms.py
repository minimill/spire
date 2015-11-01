from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError
from wtforms_components import PassiveHiddenField
from app.models import Board, Image, Color

BAD_FOLDER = 'Folder name should only contain numbers, letters, and dashes'
NO_SUCH_SLUG = 'No such slug'
SLUG_EXISTS = 'Board exists with slug "%s"'
INVALID_HEX = 'Invalid color hex'
NO_FIELD = 'No such field: "%s"'


class ValidSlug(object):
    """A validator that ensures that there is a board in the database with the
    slug that is the same as the field's data.
    :param form: The parent form
    :type form: :class:`Form`
    :param field: The field to validate
    :type field: :class:`Field`
    """

    def __call__(self, form, field):
        board = Board.query.filter_by(slug=field.data).first()
        if not board:
            raise ValidationError(NO_SUCH_SLUG)


class UniqueSlug(ValidSlug):

    def __init__(self, old_slug_fieldname):
        self.old_slug_fieldname = old_slug_fieldname

    def __call__(self, form, field):
        """A validator that ensures that there is no board in the database with the
        slug that is the same as the field's data.
        :param form: The parent form
        :type form: :class:`Form`
        :param field: The field to validate
        :type field: :class:`Field`
        """
        if not hasattr(form, self.old_slug_fieldname):
            raise ValidationError(NO_FIELD % self.old_slug_fieldname)
        old_slug_field = getattr(form, self.old_slug_fieldname)

        if field.data != old_slug_field.data:
            board = Board.query.filter_by(slug=field.data).first()
            if board:
                raise ValidationError(SLUG_EXISTS % field.data)
        else:
            super(UniqueSlug, self).__call__(form, field)


class ValidId(object):

    def __init__(self, model):
        self.model = model

    def __call__(self, form, field):
        instance = self.model.query.filter_by(id=field.data).first()
        if not instance:
            raise ValidationError('No such %s' % self.model.__class__.__name__)


class ValidImageId(ValidId):
    def __init__(self):
        super(ValidImageId, self).__init__(Image)


class ValidColorId(ValidId):
    def __init__(self):
        super(ValidColorId, self).__init__(Color)


class SpireForm(Form):

    def __init__(self, *args, **kwargs):
        super(SpireForm, self).__init__(prefix=self._prefix, *args, **kwargs)

    @property
    def _prefix(self):
        raise NotImplemented


class EditBoardForm(SpireForm):
    _prefix = 'board-'
    title = StringField('Project Name')
    old_slug = PassiveHiddenField('old-slug', [DataRequired()])
    slug = StringField('slug', [DataRequired(), UniqueSlug('old_slug')])


class TextForm(SpireForm):
    _placeholder = 'Insert an image link / hex code or drag and drop a file'
    _prefix = 'text-'
    slug = StringField('slug', [DataRequired(), ValidSlug()])
    text = StringField(_placeholder, [DataRequired()])


class ImageForm(SpireForm):
    _prefix = 'image-'
    slug = StringField('slug', [DataRequired(), ValidSlug()])
    filename = StringField('filename', [DataRequired()])


class DeleteImageForm(SpireForm):
    _prefix = 'delete-image-'
    id = StringField('id', [DataRequired(), ValidImageId()])


class DeleteColorForm(SpireForm):
    _prefix = 'delete-color-'
    id = StringField('id', [DataRequired(), ValidColorId()])


def get_forms(board):
    return {
        'board': EditBoardForm(title=board.title,
                               slug=board.slug,
                               old_slug=board.slug),
        'text': TextForm(slug=board.slug),
        'image': ImageForm(slug=board.slug),
        'delete_image': DeleteImageForm(),
        'delete_color': DeleteColorForm()
    }
