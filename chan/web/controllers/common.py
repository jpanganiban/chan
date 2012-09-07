from flask import Blueprint, jsonify, abort
from chan.core import objects


app = Blueprint('common', __name__)


@app.route('/<board>')
def board(board):
    """Show board info and threads"""
    board = objects.Board(board)
    return jsonify(board.to_dict())


@app.route('/<board>/<thread_id>')
def board_thread(board, thread_id):
    thread = objects.Thread(board, thread_id)
    if not thread:
        abort(404)
    return jsonify(thread.to_dict())
