from marshmallow import ValidationError

from schemas import BookSchema
from models import db, Book
from flask import request, jsonify, Blueprint

book_schema = BookSchema()
library = Blueprint("library", __name__)

@library.route("/")
def index():
    return jsonify({"message": "Main paige of API, hi!"})


@library.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    try:
        validated_book_data = book_schema.load(data)
        book = Book(**validated_book_data)
        db.session.add(book)
        db.session.commit()
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 422
    return jsonify(book_schema.dump(book)), 201


@library.route("/books", methods=["GET"])
def get_books():
    limit = request.args.get('limit', default=2, type=int)
    cursor = request.args.get('cursor', default=None, type=int)
    query = Book.query.order_by(Book.id.desc())
    total_books = query.count()

    if cursor:
        query = query.filter(Book.id > cursor)

    result = query.limit(limit).all()

    next_cursor = result[-1].id if len(result) == limit else None

    return jsonify({
        "total_books": total_books,
        "books": BookSchema(many=True).dump(result),
        "next_cursor": next_cursor
    })

@library.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    book = db.get_or_404(Book, book_id)
    return jsonify(book_schema.dump(book)), 200


@library.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.get_or_404(Book, book_id)
    db.session.delete(book)
    db.session.commit()
    return {}, 204
