from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime
from book_scraper import fetch_books_from_web, get_category_url

scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/api/v1/books/<category>', methods=['GET'])

def get_books(category):
    today = datetime.now().strftime('%y%m%d')
    filename = f"{category}_{today}.json"

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return jsonify(json.load(f))

    target_url = get_category_url(category)
    if not target_url:
        return jsonify({'error': f"Category {category} hittades inte."}), 404

    books_data = fetch_books_from_web(target_url)

    with open(filename, 'w') as f:
        json.dump(books_data, f, indent=4)

    return jsonify({"message": "Ny scraping klar!", "books": books_data})

@scraper_bp.route('/api/v1/books/<category>/<book_id>', methods=['DELETE'])
def delete_book(category, book_id):
    today = datetime.now().strftime('%y%m%d')
    filename = f"{category}_{today}.json"

    if not os.path.exists(filename):
        return jsonify({'error': "Ingen data finns. Gör en GET först."}), 404

    with open(filename, 'r') as f:
        books = json.load(f)

    new_books = [book for book in books if book['id'] != book_id]
    if len(books) == len(new_books):
        return jsonify({"error": "Boken hittades inte"}), 404

    with open(filename, 'w') as f:
        json.dump(new_books, f, indent=4)

    return jsonify({"message": f"Bok {book_id} borttagen", "count": len(new_books)})


@scraper_bp.route('/api/v1/books/<category>', methods=['POST'])
def add_book(category):
    today = datetime.now().strftime('%y%m%d')
    filename = f"{category}_{today}.json"

    if not os.path.exists(filename):
        return jsonify({"error": "Ingen data finns. Gör en GET först"}), 404

    new_data = request.get_json()

    with open(filename, 'r') as f:
        books = json.load(f)


    new_id = f"book_{len(books) + 1}"
    new_data['id'] = new_id

    books.append(new_data)

    with open(filename, 'w') as f:
        json.dump(books, f, indent=4)

    return jsonify({"message": "Bok tillagd", "books": new_data}), 201

@scraper_bp.route('/api/v1/books/<category>/<book_id>', methods=['PUT'])
def update_book(category, book_id):
    today = datetime.now().strftime('%y%m%d')
    filename = f"{category}_{today}.json"

    if not os.path.exists(filename):
        return jsonify({"error": "Ingen data finns. Gör en GET först."}), 404

    updates = request.get_json()

    with open(filename, 'r') as f:
        books = json.load(f)

    book_found = False
    for book in books:
        if book['id'] == book_id:
            book.update(updates)
            book_found = True
            break

    if not book_found:
        return jsonify({"error": "Boken hittades inte"}), 404

    with open(filename, 'w') as f:
        json.dump(books, f, indent=4)

    return jsonify({"message": f"Bok {book_id}) uppdaterad", "book": updates})