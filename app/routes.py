from flask import render_template, abort, redirect, url_for, jsonify
from app.lib.aws import new_aws_formdata
from app.models import Board, Color
from app.forms import get_forms, EditBoardForm, TextForm


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
            return jsonify({
                'slug': board.slug,
                'success': True,
            })
        print "error: ", board_form.errors
        abort(400)

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
            return jsonify({
                'success': True
            })

        print form.errors
        return jsonify({
            'success': False
        })
