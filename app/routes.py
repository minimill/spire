from flask import render_template, abort, redirect, url_for
from app.lib.aws import new_aws_formdata
from app.lib.json_response import json_success, json_error_message
from app.models import Board, Color, Image
from app.forms import get_forms, EditBoardForm, TextForm, ImageForm


def register_routes(app, db):

    @app.errorhandler(404)
    def handle_404(e):
        return "404", 404

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
        aws = new_aws_formdata()
        return render_template('board.html', board=board, aws=aws, forms=forms)

    @app.route('/<board_slug>', methods=['POST'])
    def save_board(board_slug):
        board = Board.query.filter_by(slug=board_slug).first()
        if not board:
            abort(404)

        board_form = EditBoardForm()
        if board_form.validate_on_submit():
            board.title = board_form.title.data
            board.slug = board_form.slug.data
            db.session.commit()
            return json_success({
                'slug': board.slug,
                'title': board.title,
            })

        return json_error_message('Failed to save board',
                                  error_data=board_form.errors)

    @app.route('/<board_slug>/text/', methods=['POST'])
    def add_text(board_slug):
        print 'add_text: ', board_slug
        board = Board.query.filter_by(slug=board_slug).first()
        if not board:
            abort(404)

        form = TextForm()
        if form.validate_on_submit():
            color = Color(hex_rep=form.text.data)
            db.session.add(color)
            board.colors.append(color)
            db.session.commit()
            return json_success({
                'hex': color.hex
            })

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
                'filename': image.filename
            })

        return json_error_message('Failed to create image',
                                  error_data=form.errors)
