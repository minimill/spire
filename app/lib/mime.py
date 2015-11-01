
class MIMEType(object):
    PNG = 'image/png'
    JPEG = 'image/jpeg'
    GIF = 'image/gif'
    BMP = 'image/bmp'
    SVG = 'image/svg+xml'
    IMAGES = (PNG, JPEG, GIF, BMP, SVG)
    HTML = 'text/html'

    EXTENSIONS = {
        PNG: '.png',
        JPEG: '.jpeg',
        GIF: '.gif',
        BMP: '.bmp',
        SVG: '.svg',
        HTML: '.html'
    }

    @classmethod
    def get_extension(cls, mimetype):
        return MIMEType.EXTENSIONS[mimetype]
