import pandas as pd
import os


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BOOKS_PATH = os.path.join(
    BASE_DIR, "data", "BX-Books.csv"
)

RATINGS_PATH = os.path.join(
    BASE_DIR, "data", "BX-Book-Ratings-Subset.csv"
)

USERS_PATH = os.path.join(
    BASE_DIR, "data", "BX-Users.csv"
)

PROCESSED_DIR = os.path.join(
    BASE_DIR, "data", "processed"
)


# ---------------------------------------------------------
# LOAD BOOK DATA
# ---------------------------------------------------------

def load_books():

    books = pd.read_csv(
        BOOKS_PATH,
        sep=";",
        encoding="latin-1",
        on_bad_lines="skip"
    )

    books.columns = [
        "ISBN",
        "Book-Title",
        "Book-Author",
        "Year-Of-Publication",
        "Publisher",
        "Image-URL-S",
        "Image-URL-M",
        "Image-URL-L"
    ]

    return books


# ---------------------------------------------------------
# LOAD RATINGS
# ---------------------------------------------------------

def load_ratings():

    ratings = pd.read_csv(
        RATINGS_PATH,
        sep=";",
        encoding="latin-1",
        on_bad_lines="skip"
    )

    ratings.columns = [
        "User-ID",
        "ISBN",
        "Book-Rating"
    ]

    return ratings


# ---------------------------------------------------------
# LOAD USERS
# ---------------------------------------------------------

def load_users():

    users = pd.read_csv(
        USERS_PATH,
        sep=";",
        encoding="latin-1",
        on_bad_lines="skip"
    )

    users.columns = [
        "User-ID",
        "Location",
        "Age"
    ]

    return users


# ---------------------------------------------------------
# CLEAN BOOK DATA
# ---------------------------------------------------------

def clean_books(books):

    books = books.copy()

    # Remove duplicate ISBNs
    books = books.drop_duplicates(
        subset="ISBN"
    )

    # Remove books without title
    books = books[
        books["Book-Title"].notna()
    ]

    # Convert title/author/publisher to strings
    books["Book-Title"] = (
        books["Book-Title"]
        .astype(str)
        .str.strip()
    )

    books["Book-Author"] = (
        books["Book-Author"]
        .fillna("Unknown Author")
        .astype(str)
        .str.strip()
    )

    books["Publisher"] = (
        books["Publisher"]
        .fillna("Unknown Publisher")
        .astype(str)
        .str.strip()
    )

    return books


# ---------------------------------------------------------
# CLEAN RATINGS
# ---------------------------------------------------------

def clean_ratings(ratings):

    ratings = ratings.copy()

    # Convert rating to numeric
    ratings["Book-Rating"] = pd.to_numeric(
        ratings["Book-Rating"],
        errors="coerce"
    )

    ratings = ratings.dropna(
        subset=["User-ID", "ISBN", "Book-Rating"]
    )

    # Keep explicit ratings only
    # Book-Crossing uses 0 for implicit interactions
    ratings = ratings[
        ratings["Book-Rating"] > 0
    ]

    # Keep valid 1-10 ratings
    ratings = ratings[
        ratings["Book-Rating"].between(1, 10)
    ]

    # Remove duplicate user-book ratings
    ratings = ratings.drop_duplicates(
        subset=["User-ID", "ISBN"]
    )

    return ratings


# ---------------------------------------------------------
# MERGE BOOKS + RATINGS
# ---------------------------------------------------------

def create_master_dataset():

    print("\nLoading datasets...")

    books = load_books()
    ratings = load_ratings()

    print(f"Books loaded:   {len(books):,}")
    print(f"Ratings loaded: {len(ratings):,}")

    print("\nCleaning datasets...")

    books = clean_books(books)
    ratings = clean_ratings(ratings)

    print(f"Books after cleaning:   {len(books):,}")
    print(f"Ratings after cleaning: {len(ratings):,}")

    # -----------------------------------------------------
    # Merge using ISBN
    # -----------------------------------------------------

    master = ratings.merge(
        books,
        on="ISBN",
        how="inner"
    )

    print(
        f"\nMaster dataset rows: {len(master):,}"
    )

    # -----------------------------------------------------
    # Create processed directory
    # -----------------------------------------------------

    os.makedirs(
        PROCESSED_DIR,
        exist_ok=True
    )

    output_path = os.path.join(
        PROCESSED_DIR,
        "master_books.csv"
    )

    master.to_csv(
        output_path,
        index=False,
        encoding="utf-8"
    )

    print(
        f"\nSaved processed dataset to:\n{output_path}"
    )

    return master


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    master_df = create_master_dataset()

    print("\n--------------------------------")
    print("DATASET READY")
    print("--------------------------------")

    print("\nColumns:")
    print(master_df.columns.tolist())

    print("\nFirst 5 rows:")
    print(master_df.head())

    print("\nRating distribution:")
    print(
        master_df["Book-Rating"]
        .value_counts()
        .sort_index()
    )