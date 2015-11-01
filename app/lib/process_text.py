import requests
import os
from app import app, db, s3
from app.models import Color, TextBlock, Image
from app.lib.aws import iso_timestamp
from app.lib.mime import MIMEType


def _download_image_at_url(url):
    resp = requests.get(url, stream=True)
    if not resp.ok:
        return ValueError

    content_type = resp.headers['Content-Type']
    filename = iso_timestamp() + MIMEType.get_extension(content_type)
    local_path = app.config['UPLOAD_FOLDER'] + filename

    with open(local_path, 'wb') as tmp_image:
        for chunk in resp.iter_content(1024):
            tmp_image.write(chunk)

    return local_path, filename


def _process_text_as_url(board, url):
    resp = requests.head(url)
    content_type = resp.headers['Content-Type']
    if content_type in MIMEType.IMAGES:
        local_path, filename = _download_image_at_url(url)
        s3.upload_to_s3(local_path, filename, content_type)
        os.remove(local_path)
        image = Image(filename='uploads/' + filename)
        db.session.add(image)
        board.images.append(image)
        return {
            'image': {
                'url': image.url,
                'id': image.id
            }
        }
    elif content_type == MIMEType.HTML:
        raise ValueError('Non-Image URLs not supported')
        # website = Website()
        # return {
        #     'website': {
        #         website.dict()
        #     }
        # }
    else:
        raise ValueError('Unkown Content-Type: "%s"' % content_type)


def process_text(board, text):
    if Color.is_valid_hex(text):
        color = Color(hex=text)
        db.session.add(color)
        board.colors.append(color)
        return {
            'color': {
                'hex': color.hex,
                'id': color.id
            }
        }
    else:
        try:
            return _process_text_as_url(board, text)
        except ValueError:
            print "ValueError"
            text_block = TextBlock(text=text)
            db.session.add(text_block)
            board.text_blocks.append(text_block)
            return {
                'text_block': text_block.text
            }
