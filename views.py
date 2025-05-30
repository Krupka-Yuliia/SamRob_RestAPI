from flask import request, jsonify, Blueprint, url_for
from marshmallow import ValidationError

from models import db, Book
from schemas import BookSchema

book_schema = BookSchema()
library = Blueprint("library", __name__)


def get_book_links(book_id):
    return {
        "self": {"href": url_for('library.get_book', book_id=book_id)},
        "delete": {"href": url_for('library.delete_book', book_id=book_id)},
        "list": {"href": url_for('library.get_books')}
    }


def get_book_or_404(book_id):
    book = Book.query.get(book_id)
    if not book:
        response = {
            "error": f"Book with id {book_id} not found",
            "_links": {
                "list": {"href": url_for('library.get_books')}
            }
        }
        return None, (jsonify(response), 404)
    return book, None


@library.route("/")
def index():
    return jsonify({
        "message": "Main page of API, hi!",
        "_links": {
            "self": {"href": url_for('library.index')},
            "get_books": {"href": url_for('library.get_books')},
            "create_book": {"href": url_for('library.create_book')},
            "get_book": {"href": url_for('library.get_book', book_id=9)},
            "delete_book": {"href": url_for('library.delete_book', book_id=9)},
        }
    })


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

    book_data = book_schema.dump(book)
    book_data['_links'] = get_book_links(book.id)
    return jsonify(book_data), 201


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

    books_data = BookSchema(many=True).dump(result)

    for book in books_data:
        book['_links'] = {
            "self": {"href": url_for('library.get_book', book_id=book['id'])},
            "delete": {"href": url_for('library.delete_book', book_id=book['id'])},
        }

    response = {
        "total_books": total_books,
        "books": books_data,
        "next_cursor": next_cursor,
        "_links": {
            "self": {"href": url_for('library.get_books')},
            "create": {"href": url_for('library.create_book')}
        }
    }

    return jsonify(response)


@library.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book, error_response = get_book_or_404(book_id)
    if error_response:
        return error_response

    book_data = book_schema.dump(book)
    book_data['_links'] = get_book_links(book_id)
    return jsonify(book_data), 200


@library.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book, error_response = get_book_or_404(book_id)
    if error_response:
        return error_response

    db.session.delete(book)
    db.session.commit()
    return {}, 204
