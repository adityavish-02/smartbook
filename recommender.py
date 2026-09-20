import os
import joblib
import numpy as np
import pandas as pd


class BookRecommender:

    def __init__(self):

        # ==================================================
        # PATHS
        # ==================================================

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        model_dir = os.path.join(
            base_dir,
            "models"
        )

        # ==================================================
        # LOAD BOOK METADATA
        # ==================================================

        books_path = os.path.join(
            model_dir,
            "books_metadata.csv"
        )

        self.books = pd.read_csv(
            books_path,
            encoding="utf-8"
        )

        # Make sure ISBN is string
        self.books["ISBN"] = (
            self.books["ISBN"]
            .astype(str)
            .str.strip()
        )

        # ==================================================
        # LOAD CONTENT MODEL
        # ==================================================

        content_path = os.path.join(
            model_dir,
            "content_model.joblib"
        )

        content_model = joblib.load(
            content_path
        )

        self.tfidf = content_model[
            "tfidf"
        ]

        self.tfidf_matrix = content_model[
            "tfidf_matrix"
        ]

        self.content_index = content_model[
            "isbn_to_index"
        ]

        # ==================================================
        # LOAD COLLABORATIVE MODEL
        # ==================================================

        collaborative_path = os.path.join(
            model_dir,
            "collaborative_model.joblib"
        )

        collaborative_model = joblib.load(
            collaborative_path
        )

        self.svd = collaborative_model[
            "svd"
        ]

        self.book_latent = collaborative_model[
            "book_latent"
        ]

        self.collaborative_index = (
            collaborative_model[
                "isbn_to_index"
            ]
        )

        print(
            f"Loaded {len(self.books):,} books."
        )

    # ======================================================
    # SEARCH BOOKS
    # ======================================================

    def search_books(
        self,
        query,
        limit=10
    ):

        if not query:
            return []

        query = str(query).strip().lower()

        if not query:
            return []

        # ----------------------------------------------
        # Exact title matches first
        # ----------------------------------------------

        exact = self.books[
            self.books["Book-Title"]
            .str.lower()
            .eq(query)
        ]

        # ----------------------------------------------
        # Partial title matches
        # ----------------------------------------------

        partial = self.books[
            self.books["Book-Title"]
            .str.lower()
            .str.contains(
                query,
                regex=False,
                na=False
            )
        ]

        # Combine exact + partial
        results = pd.concat(
            [exact, partial]
        ).drop_duplicates(
            subset=["ISBN"]
        )

        # ----------------------------------------------
        # Sort by popularity
        # ----------------------------------------------

        if "rating_count" in results.columns:

            results = results.sort_values(
                by=[
                    "rating_count",
                    "average_rating"
                ],
                ascending=False
            )

        results = results.head(
            limit
        )

        return self._format_books(
            results
        )

    # ======================================================
    # GET BOOK BY ISBN
    # ======================================================

    def get_book(
        self,
        isbn
    ):

        isbn = str(isbn).strip()

        result = self.books[
            self.books["ISBN"] == isbn
        ]

        if result.empty:
            return None

        return self._format_books(
            result.head(1)
        )[0]

    # ======================================================
    # CONTENT-BASED RECOMMENDATIONS
    # ======================================================

    def content_recommendations(
        self,
        isbn,
        limit=10
    ):

        isbn = str(isbn).strip()

        if isbn not in self.content_index:
            return []

        index = self.content_index[
            isbn
        ]

        # Since TF-IDF vectors were normalized,
        # dot product gives cosine similarity.
        similarities = (
            self.tfidf_matrix
            @ self.tfidf_matrix[index].T
        ).toarray().flatten()

        # Sort highest similarity first
        similar_indices = np.argsort(
            similarities
        )[::-1]

        recommendations = []

        for idx in similar_indices:

            if idx == index:
                continue

            score = float(
                similarities[idx]
            )

            if score <= 0:
                continue

            book = self.books.iloc[
                idx
            ].copy()

            book["content_score"] = score

            recommendations.append(
                book
            )

            if len(recommendations) >= limit:
                break

        if not recommendations:
            return []

        result = pd.DataFrame(
            recommendations
        )

        return self._format_books(
            result
        )

    # ======================================================
    # COLLABORATIVE RECOMMENDATIONS
    # ======================================================

    def collaborative_recommendations(
        self,
        isbn,
        limit=10
    ):

        isbn = str(isbn).strip()

        if isbn not in self.collaborative_index:
            return []

        index = self.collaborative_index[
            isbn
        ]

        target_vector = (
            self.book_latent[index]
        )

        # Since latent vectors are normalized,
        # dot product gives cosine similarity.
        similarities = (
            self.book_latent
            @ target_vector
        )

        similar_indices = np.argsort(
            similarities
        )[::-1]

        recommendations = []

        for idx in similar_indices:

            if idx == index:
                continue

            score = float(
                similarities[idx]
            )

            if score <= 0:
                continue

            book = self.books.iloc[
                idx
            ].copy()

            book[
                "collaborative_score"
            ] = score

            recommendations.append(
                book
            )

            if len(recommendations) >= limit:
                break

        if not recommendations:
            return []

        result = pd.DataFrame(
            recommendations
        )

        return self._format_books(
            result
        )

    # ======================================================
    # HYBRID RECOMMENDATIONS
    # ======================================================

    def hybrid_recommendations(
        self,
        isbn,
        limit=10,
        content_weight=0.60,
        collaborative_weight=0.40
    ):

        isbn = str(isbn).strip()

        if isbn not in self.content_index:
            return []

        if isbn not in self.collaborative_index:
            return self.content_recommendations(
                isbn,
                limit
            )

        # ----------------------------------------------
        # CONTENT SIMILARITY
        # ----------------------------------------------

        content_index = (
            self.content_index[isbn]
        )

        content_scores = (
            self.tfidf_matrix
            @ self.tfidf_matrix[
                content_index
            ].T
        ).toarray().flatten()

        # ----------------------------------------------
        # COLLABORATIVE SIMILARITY
        # ----------------------------------------------

        collaborative_index = (
            self.collaborative_index[isbn]
        )

        collaborative_scores = (
            self.book_latent
            @ self.book_latent[
                collaborative_index
            ]
        )

        # ----------------------------------------------
        # NORMALIZE SCORES
        # ----------------------------------------------

        content_scores = self._normalize_scores(
            content_scores
        )

        collaborative_scores = (
            self._normalize_scores(
                collaborative_scores
            )
        )

        # ----------------------------------------------
        # HYBRID SCORE
        # ----------------------------------------------

        hybrid_scores = (
            content_weight
            * content_scores
            +
            collaborative_weight
            * collaborative_scores
        )

        # Don't recommend the selected book itself
        hybrid_scores[
            content_index
        ] = -1

        # ----------------------------------------------
        # TOP RESULTS
        # ----------------------------------------------

        top_indices = np.argsort(
            hybrid_scores
        )[::-1]

        recommendations = []

        for idx in top_indices:

            score = float(
                hybrid_scores[idx]
            )

            if score <= 0:
                continue

            book = self.books.iloc[
                idx
            ].copy()

            book[
                "content_score"
            ] = float(
                content_scores[idx]
            )

            book[
                "collaborative_score"
            ] = float(
                collaborative_scores[idx]
            )

            book[
                "hybrid_score"
            ] = score

            recommendations.append(
                book
            )

            if len(recommendations) >= limit:
                break

        if not recommendations:
            return []

        result = pd.DataFrame(
            recommendations
        )

        return self._format_books(
            result,
            include_scores=True
        )

    # ======================================================
    # POPULAR BOOKS
    # ======================================================

    def popular_books(
        self,
        limit=10
    ):

        if "weighted_rating" not in self.books.columns:

            result = self.books.sort_values(
                by="average_rating",
                ascending=False
            )

        else:

            result = self.books.sort_values(
                by="weighted_rating",
                ascending=False
            )

        result = result.head(
            limit
        )

        return self._format_books(
            result
        )

    # ======================================================
    # NORMALIZE SCORES
    # ======================================================

    def _normalize_scores(
        self,
        scores
    ):

        scores = np.asarray(
            scores,
            dtype=float
        )

        min_score = scores.min()
        max_score = scores.max()

        if max_score == min_score:

            return np.zeros_like(
                scores
            )

        return (
            scores - min_score
        ) / (
            max_score - min_score
        )

    # ======================================================
    # FORMAT BOOK DATA
    # ======================================================

    def _format_books(
        self,
        dataframe,
        include_scores=False
    ):

        results = []

        for _, row in dataframe.iterrows():

            book = {
                "isbn": str(
                    row.get(
                        "ISBN",
                        ""
                    )
                ),

                "title": str(
                    row.get(
                        "Book-Title",
                        "Unknown Title"
                    )
                ),

                "author": str(
                    row.get(
                        "Book-Author",
                        "Unknown Author"
                    )
                ),

                "publisher": str(
                    row.get(
                        "Publisher",
                        "Unknown Publisher"
                    )
                ),

                "year": str(
                    row.get(
                        "Year-Of-Publication",
                        ""
                    )
                ),

                "image_small": str(
                    row.get(
                        "Image-URL-S",
                        ""
                    )
                ),

                "image_medium": str(
                    row.get(
                        "Image-URL-M",
                        ""
                    )
                ),

                "image_large": str(
                    row.get(
                        "Image-URL-L",
                        ""
                    )
                ),

                "rating": round(
                    float(
                        row.get(
                            "average_rating",
                            0
                        )
                    ),
                    2
                ),

                "rating_count": int(
                    row.get(
                        "rating_count",
                        0
                    )
                )
            }

            if include_scores:

                book["content_score"] = round(
                    float(
                        row.get(
                            "content_score",
                            0
                        )
                    ),
                    4
                )

                book[
                    "collaborative_score"
                ] = round(
                    float(
                        row.get(
                            "collaborative_score",
                            0
                        )
                    ),
                    4
                )

                book["hybrid_score"] = round(
                    float(
                        row.get(
                            "hybrid_score",
                            0
                        )
                    ),
                    4
                )

            results.append(
                book
            )

        return results


# ==========================================================
# QUICK TEST
# ==========================================================

if __name__ == "__main__":

    recommender = BookRecommender()

    print("\n===================================")
    print("SMARTBOOK RECOMMENDER TEST")
    print("===================================")

    # ----------------------------------------------
    # Search test
    # ----------------------------------------------

    print("\nSearching for 'Harry Potter'...")

    search_results = recommender.search_books(
        "Harry Potter",
        limit=5
    )

    for book in search_results:

        print(
            f"- {book['title']} "
            f"by {book['author']}"
        )

    # ----------------------------------------------
    # Popular books test
    # ----------------------------------------------

    print("\nPopular books:")

    popular = recommender.popular_books(
        limit=5
    )

    for book in popular:

        print(
            f"- {book['title']} "
            f"| Rating: {book['rating']}"
        )