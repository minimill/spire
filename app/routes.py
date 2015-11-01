import os
from flask import (render_template, abort, redirect, url_for,
                   send_from_directory)
from app import s3
from app.models import Board, Image, Color
from app.forms import (get_forms, EditBoardForm, TextForm, ImageForm,
                       DeleteImageForm, DeleteColorForm)
from app.lib.process_text import process_text
from app.lib.json_response import json_success, json_error_message


def register_routes(app, db):

    @app.errorhandler(404)
    def handle_404(e):
        return "404", 404

    @app.route('/favicon.ico', methods=['GET'])
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')

    @app.route('/')
    def new():
        board = Board()
        db.session.add(board)
        db.session.commit()
        return redirect(url_for('board', board_slug=board.slug))

    @app.route('/<board_slug>', methods=['GET'])
    def board(board_slug):
        board = Board.query.filter_by(slug=board_slug).first()
        if not board:
            abort(404)

        forms = get_forms(board)
        aws = s3.new_aws_formdata()
        return render_template('board.html',
                               board=board,
                               aws=aws,
                               forms=forms)

    @app.route('/<board_slug>', methods=['POST'])
    def save_board(board_slug):
        board = Board.query.filter_by(slug=board_slug).first()
        if not board:
            abort(404)

        form = EditBoardForm()
        if form.validate_on_submit():
            board.title = form.title.data
            board.slug = form.slug.data
            db.session.commit()
            return json_success({
                'slug': board.slug,
                'title': board.title,
            })

        error_data = {
            'errors': form.errors,
            'revert': {
                'slug': board.slug,
                'title': board.title
            }
        }

        return json_error_message('Failed to save board',
                                  error_data=error_data)

    @app.route('/<board_slug>/text/', methods=['POST'])
    def add_text(board_slug):
        print 'add_text: ', board_slug
        board = Board.query.filter_by(slug=board_slug).first()
        if not board:
            abort(404)

        form = TextForm()
        if form.validate_on_submit():
            response_data = process_text(board, form.text.data)
            db.session.commit()
            return json_success(response_data)

        return json_error_message('Failed to create color',
                                  error_data=form.errors)

    @app.route('/<board_slug>/image/', methods=['POST'])
    def add_image(board_slug):
        print 'add_image: ', board_slug
        board = Board.query.filter_by(slug=board_slug).first()
        if not board:
            abort(404)

        form = ImageForm()
        if form.validate_on_submit():
            image = Image(filename=form.filename.data)
            db.session.add(image)
            board.images.append(image)
            db.session.commit()
            return json_success({
                'image': {
                    'filename': image.filename,
                    'id': image.id
                }
            })

        return json_error_message('Failed to create image',
                                  error_data=form.errors)

    @app.route('/image/delete', methods=['POST'])
    def delete_image():
        form = DeleteImageForm()
        if form.validate_on_submit():
            image = Image.query.filter_by(id=form.id.data).first()
            if not image:
                abort(404)
            db.session.delete(image)
            db.session.commit()
            return json_success({
                'deleted': image.id
            })

        return json_error_message('Failed to delete image',
                                  error_data=form.errors)

    @app.route('/color/delete', methods=['POST'])
    def delete_color():
        form = DeleteColorForm()
        if form.validate_on_submit():
            color = Color.query.filter_by(id=form.id.data).first()
            if not color:
                abort(404)
            db.session.delete(color)
            db.session.commit()
            return json_success({
                'deleted': color.id
            })

        return json_error_message('Failed to delete color',
                                  error_data=form.errors)
