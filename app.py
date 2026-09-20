from flask import Flask, render_template, request, jsonify
from recommender import BookRecommender
import os
import json

app = Flask(__name__)

# ============================================================
# LOAD RECOMMENDER
# ============================================================

recommender = BookRecommender()


# ============================================================
# HELPERS
# ============================================================

def normalize_book(book):
    """
    Convert a book object into a JSON-safe dictionary.
    """

    if book is None:
        return None

    return {
        "isbn": str(book.get("isbn", "")),
        "title": str(book.get("title", "Unknown Title")),
        "author": str(book.get("author", "Unknown Author")),
        "image_small": str(book.get("image_small", "")),
        "image_medium": str(book.get("image_medium", "")),
        "image_large": str(book.get("image_large", "")),
        "rating": float(book.get("rating", 0) or 0),
        "rating_count": int(book.get("rating_count", 0) or 0),
    }


def normalize_recommendation(book):
    """
    Normalize recommendation data while preserving
    recommendation scores.
    """

    if book is None:
        return None

    return {
        "isbn": str(book.get("isbn", "")),
        "title": str(book.get("title", "Unknown Title")),
        "author": str(book.get("author", "Unknown Author")),

        "image_small": str(book.get("image_small", "")),
        "image_medium": str(book.get("image_medium", "")),
        "image_large": str(book.get("image_large", "")),

        "rating": float(book.get("rating", 0) or 0),
        "rating_count": int(book.get("rating_count", 0) or 0),

        "content_score": float(book.get("content_score", 0) or 0),
        "collaborative_score": float(
            book.get("collaborative_score", 0) or 0
        ),
        "hybrid_score": float(book.get("hybrid_score", 0) or 0),
    }


def normalize_recommendations(books):
    return [
        normalize_recommendation(book)
        for book in books
        if book is not None
    ]


# ============================================================
# MAIN PAGE
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# SEARCH API
# ============================================================

@app.route("/api/search")
def api_search():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    try:

        results = recommender.search_books(
            query,
            limit=10
        )

        return jsonify([
            normalize_book(book)
            for book in results
        ])

    except Exception as e:

        print("SEARCH ERROR:", e)

        return jsonify({
            "error": "Search failed"
        }), 500


# ============================================================
# RECOMMENDATION API
# ============================================================

@app.route("/api/recommend/<isbn>")
def api_recommend(isbn):

    try:

        # Get selected book
        book = recommender.get_book(isbn)

        if book is None:
            return jsonify({
                "error": "Book not found"
            }), 404

        # Generate hybrid recommendations
        recommendations = recommender.hybrid_recommendations(
            isbn,
            limit=20
        )

        return jsonify({

            "book": normalize_book(book),

            "recommendations": normalize_recommendations(
                recommendations
            )

        })

    except Exception as e:

        print("RECOMMENDATION ERROR:", e)

        return jsonify({
            "error": "Could not generate recommendations"
        }), 500


# ============================================================
# OPTIONAL BOOK API
# ============================================================

@app.route("/api/book/<isbn>")
def api_book(isbn):

    try:

        book = recommender.get_book(isbn)

        if book is None:
            return jsonify({
                "error": "Book not found"
            }), 404

        return jsonify(normalize_book(book))

    except Exception as e:

        print("BOOK ERROR:", e)

        return jsonify({
            "error": "Could not retrieve book"
        }), 500


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "error": "Endpoint not found"
        }), 404

    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "error": "Internal server error"
        }), 500

    return render_template("index.html"), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )