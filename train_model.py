import os
import json
import joblib
import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "master_books.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

MIN_BOOK_RATINGS = 5
MIN_USER_RATINGS = 3

TFIDF_MAX_FEATURES = 30000

SVD_COMPONENTS = 30


# ============================================================
# LOAD DATA
# ============================================================

print("\n==========================================")
print("SMARTBOOK MODEL TRAINING")
print("==========================================")

print("\nLoading processed dataset...")

df = pd.read_csv(
    DATA_PATH,
    encoding="utf-8"
)

print(f"Initial rows: {len(df):,}")


# ============================================================
# BASIC CLEANING
# ============================================================

print("\nCleaning data...")

df["Book-Title"] = (
    df["Book-Title"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["Book-Author"] = (
    df["Book-Author"]
    .fillna("Unknown Author")
    .astype(str)
    .str.strip()
)

df["Publisher"] = (
    df["Publisher"]
    .fillna("Unknown Publisher")
    .astype(str)
    .str.strip()
)

df["ISBN"] = (
    df["ISBN"]
    .astype(str)
    .str.strip()
)

df["Book-Rating"] = pd.to_numeric(
    df["Book-Rating"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "User-ID",
        "ISBN",
        "Book-Rating"
    ]
)


# ============================================================
# REMOVE BOOKS WITH VERY FEW RATINGS
# ============================================================

print("\nFiltering books...")

book_rating_counts = (
    df.groupby("ISBN")
    .size()
)

valid_books = book_rating_counts[
    book_rating_counts >= MIN_BOOK_RATINGS
].index

df = df[
    df["ISBN"].isin(valid_books)
]

print(
    f"Books with at least "
    f"{MIN_BOOK_RATINGS} ratings: "
    f"{df['ISBN'].nunique():,}"
)


# ============================================================
# REMOVE USERS WITH VERY FEW RATINGS
# ============================================================

user_rating_counts = (
    df.groupby("User-ID")
    .size()
)

valid_users = user_rating_counts[
    user_rating_counts >= MIN_USER_RATINGS
].index

df = df[
    df["User-ID"].isin(valid_users)
]

print(
    f"Users with at least "
    f"{MIN_USER_RATINGS} ratings: "
    f"{df['User-ID'].nunique():,}"
)

print(
    f"Final ratings used for training: "
    f"{len(df):,}"
)


# ============================================================
# CREATE BOOK METADATA TABLE
# ============================================================

print("\nCreating book metadata...")

books = (
    df[
        [
            "ISBN",
            "Book-Title",
            "Book-Author",
            "Year-Of-Publication",
            "Publisher",
            "Image-URL-S",
            "Image-URL-M",
            "Image-URL-L"
        ]
    ]
    .drop_duplicates("ISBN")
    .reset_index(drop=True)
)

print(
    f"Unique books used: "
    f"{len(books):,}"
)


# ============================================================
# CONTENT-BASED MODEL
# ============================================================

print("\n==========================================")
print("TRAINING CONTENT-BASED MODEL")
print("==========================================")

# Combine important book information
books["content"] = (
    books["Book-Title"].fillna("")
    + " "
    + books["Book-Author"].fillna("")
    + " "
    + books["Publisher"].fillna("")
)

print("Creating TF-IDF vectors...")

tfidf = TfidfVectorizer(
    stop_words="english",
    max_features=TFIDF_MAX_FEATURES,
    ngram_range=(1, 2)
)

tfidf_matrix = tfidf.fit_transform(
    books["content"]
)

print(
    f"TF-IDF matrix shape: "
    f"{tfidf_matrix.shape}"
)

print("Normalizing vectors...")

tfidf_matrix = normalize(
    tfidf_matrix
)


# ============================================================
# COLLABORATIVE FILTERING MODEL
# ============================================================

print("\n==========================================")
print("TRAINING COLLABORATIVE MODEL")
print("==========================================")

print("Creating user-book matrix...")

# Convert users/books into integer indices
user_codes = pd.Categorical(
    df["User-ID"]
)

book_codes = pd.Categorical(
    df["ISBN"],
    categories=books["ISBN"]
)

user_indices = user_codes.codes
book_indices = book_codes.codes

valid_mask = (
    (user_indices >= 0)
    & (book_indices >= 0)
)

user_indices = user_indices[valid_mask]
book_indices = book_indices[valid_mask]

ratings = df["Book-Rating"].values[
    valid_mask
]

n_users = len(
    user_codes.categories
)

n_books = len(books)

print(
    f"Users: {n_users:,}"
)

print(
    f"Books: {n_books:,}"
)

print(
    f"Ratings: {len(ratings):,}"
)


# Sparse user-book matrix
user_book_matrix = csr_matrix(
    (
        ratings,
        (
            user_indices,
            book_indices
        )
    ),
    shape=(
        n_users,
        n_books
    )
)

print(
    f"User-book matrix shape: "
    f"{user_book_matrix.shape}"
)


# ============================================================
# SVD
# ============================================================

print("\nApplying Truncated SVD...")

n_components = min(
    SVD_COMPONENTS,
    min(user_book_matrix.shape) - 1
)

svd = TruncatedSVD(
    n_components=n_components,
    random_state=42
)

user_latent = svd.fit_transform(
    user_book_matrix
)

# Convert user-book matrix into
# latent representation of books
book_latent = svd.components_.T

book_latent = normalize(
    book_latent
)

print(
    f"Latent book matrix shape: "
    f"{book_latent.shape}"
)

print(
    f"Explained variance: "
    f"{svd.explained_variance_ratio_.sum():.2%}"
)


# ============================================================
# POPULARITY INFORMATION
# ============================================================

print("\nCalculating popularity...")

book_stats = (
    df.groupby("ISBN")
    .agg(
        rating_count=(
            "Book-Rating",
            "count"
        ),
        average_rating=(
            "Book-Rating",
            "mean"
        )
    )
    .reset_index()
)

# Weighted rating
global_mean = df[
    "Book-Rating"
].mean()

C = 20

book_stats["weighted_rating"] = (
    (
        book_stats["rating_count"]
        /
        (
            book_stats["rating_count"]
            + C
        )
    )
    *
    book_stats["average_rating"]
    +
    (
        C
        /
        (
            book_stats["rating_count"]
            + C
        )
    )
    *
    global_mean
)

books = books.merge(
    book_stats,
    on="ISBN",
    how="left"
)


# ============================================================
# SAVE BOOK METADATA
# ============================================================

books_path = os.path.join(
    MODEL_DIR,
    "books_metadata.csv"
)

books.to_csv(
    books_path,
    index=False,
    encoding="utf-8"
)

print(
    f"\nSaved book metadata:"
    f"\n{books_path}"
)


# ============================================================
# SAVE CONTENT MODEL
# ============================================================

content_model = {
    "tfidf": tfidf,
    "tfidf_matrix": tfidf_matrix,
    "isbn_to_index": {
        isbn: index
        for index, isbn
        in enumerate(books["ISBN"])
    }
}

content_path = os.path.join(
    MODEL_DIR,
    "content_model.joblib"
)

joblib.dump(
    content_model,
    content_path
)

print(
    f"Saved content model:"
    f"\n{content_path}"
)


# ============================================================
# SAVE COLLABORATIVE MODEL
# ============================================================

collaborative_model = {
    "svd": svd,
    "book_latent": book_latent,
    "isbn_to_index": {
        isbn: index
        for index, isbn
        in enumerate(books["ISBN"])
    }
}

collaborative_path = os.path.join(
    MODEL_DIR,
    "collaborative_model.joblib"
)

joblib.dump(
    collaborative_model,
    collaborative_path
)

print(
    f"Saved collaborative model:"
    f"\n{collaborative_path}"
)


# ============================================================
# SAVE TRAINING INFORMATION
# ============================================================

metadata = {
    "books": int(len(books)),
    "users": int(n_users),
    "ratings": int(len(ratings)),
    "tfidf_features": int(
        tfidf_matrix.shape[1]
    ),
    "svd_components": int(
        n_components
    ),
    "global_rating": float(
        global_mean
    )
}

metadata_path = os.path.join(
    MODEL_DIR,
    "model_metadata.json"
)

with open(
    metadata_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        indent=4
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n==========================================")
print("MODEL TRAINING COMPLETE")
print("==========================================")

print(
    f"\nBooks:       {len(books):,}"
)

print(
    f"Users:       {n_users:,}"
)

print(
    f"Ratings:     {len(ratings):,}"
)

print(
    f"TF-IDF:      {tfidf_matrix.shape}"
)

print(
    f"SVD factors: {n_components}"
)

print("\nModels saved successfully.")