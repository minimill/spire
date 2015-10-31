
class MIMEType(object):
    PNG = 'image/png'
    JPEG = 'image/jpeg'
    GIF = 'image/gif'
    BMP = 'image/bmp'
    IMAGES = (PNG, JPEG, GIF, BMP)
    HTML = 'text/html'

    EXTENSIONS = {
        PNG: '.png',
        JPEG: '.jpeg',
        GIF: '.gif',
        BMP: '.bmp',
        HTML: '.html'
    }

    @classmethod
    def get_extension(cls, mimetype):
        return MIMEType.EXTENSIONS[mimetype]
