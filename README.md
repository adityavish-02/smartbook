# 📚 SmartBook — Hybrid Book Recommendation System

> An AI-powered book recommendation system that combines content-based filtering and collaborative filtering to discover books similar to what a reader already enjoys.

## 🚀 Overview

SmartBook is a hybrid book recommendation system designed to provide intelligent book recommendations using two complementary approaches:

- 📖 **Content-Based Filtering** — finds books with similar characteristics to the selected book.
- 👥 **Collaborative Filtering** — uses reader rating patterns to identify books preferred by similar readers.
- 🧠 **Hybrid Recommendation** — combines both signals to produce the final recommendation ranking.

The system is deployed as an interactive **Flask web application** where users can search for a book, select it, and immediately receive a ranked list of recommendations.

## ✨ Features

- 🔎 Intelligent book search
- 📚 Book selection with cover, author, and rating information
- 🧠 Hybrid recommendation engine
- 📖 Content-based similarity
- 👥 Collaborative filtering
- 📊 Recommendation score breakdown
- ⚡ Interactive single-page interface
- 🎨 Modern responsive UI
- 🔄 Select a recommended book to generate a new recommendation set
- 🖼️ Book cover integration
- ⭐ Rating information
- 🐍 Python + Flask backend
- 🤖 Scikit-learn based machine learning pipeline

## 🧠 Recommendation Approach

SmartBook uses a **hybrid recommendation strategy**.

Instead of relying on only one recommendation technique, the system combines content similarity and reader behavior.

### 1. Content-Based Filtering

Content-based filtering recommends books based on the similarity between their available textual and book metadata information.

The system uses **TF-IDF vectorization** to represent book information numerically.

```text
Book Information
      ↓
Text Processing
      ↓
TF-IDF Vectorization
      ↓
Book Feature Vectors
      ↓
Similarity Calculation
      ↓
Content Recommendations
```

### 2. Collaborative Filtering

Collaborative filtering uses patterns in user-book ratings.

Instead of only asking what information a book contains, collaborative filtering considers patterns in reader preferences.

The project uses **Singular Value Decomposition (SVD)** to represent rating behavior in a lower-dimensional latent space.

```text
User Ratings
      ↓
User-Book Rating Matrix
      ↓
SVD
      ↓
Latent Representation
      ↓
Book Similarity
      ↓
Collaborative Recommendations
```

### 3. Hybrid Recommendation

The final recommendation score combines the two recommendation signals.

```text
Hybrid Score
    =
0.60 × Content Score
    +
0.40 × Collaborative Score
```

Therefore:

```text
60% Content Similarity
        +
40% Reader Similarity
        ↓
Final Hybrid Ranking
```

This allows SmartBook to consider both book characteristics and patterns in reader preferences.

## 📊 Model Statistics

The current trained recommendation system contains approximately:

| Component | Value |
|---|---:|
| Books | 2,125 |
| Users | 7,579 |
| Ratings | 67,234 |
| TF-IDF Features | 10,529 |
| SVD Latent Factors | 30 |

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │        User          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Flask Web App     │
                    │       app.py         │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │   Book Search   │        │  Recommendation │
        │                 │        │     Request     │
        └────────┬────────┘        └────────┬────────┘
                 │                          │
                 └────────────┬─────────────┘
                              ▼
                    ┌──────────────────────┐
                    │   BookRecommender    │
                    │   recommender.py     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
    ┌────────────────────┐          ┌────────────────────┐
    │ Content-Based      │          │ Collaborative      │
    │ Recommendation     │          │ Recommendation     │
    │                    │          │                    │
    │ TF-IDF             │          │ SVD                │
    │ Similarity         │          │ Latent Factors     │
    └──────────┬─────────┘          └──────────┬─────────┘
               │                               │
               └──────────────┬────────────────┘
                              ▼
                    ┌──────────────────────┐
                    │   Hybrid Ranking     │
                    │                      │
                    │ 60% Content          │
                    │ 40% Collaborative    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Recommended Books    │
                    └──────────────────────┘
```

## 🖥️ Application Flow

SmartBook follows a single-page recommendation workflow:

```text
Search for a Book
       ↓
Select a Book
       ↓
Analyze Book
       ↓
Generate Content Similarity
       +
Generate Reader Similarity
       ↓
Calculate Hybrid Scores
       ↓
Rank Recommendations
       ↓
Display Recommended Books
```

Users can also select one of the recommended books and use it as the new input for another recommendation cycle.

## 📁 Project Structure

```text
SmartBook/
│
├── app.py
├── config.py
├── data_processor.py
├── recommender.py
├── train_model.py
├── requirements.txt
├── .gitignore
│
├── models/
│   ├── trained model files
│   ├── TF-IDF artifacts
│   ├── SVD artifacts
│   └── model metadata
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
└── templates/
    └── index.html
```

> The raw `data/` directory is excluded from the Git repository because the dataset is large. The trained model artifacts are stored in `models/`.

## 🛠️ Tech Stack

### Programming

- Python

### Machine Learning

- NumPy
- Pandas
- Scikit-learn
- SciPy
- Joblib

### Recommendation Techniques

- TF-IDF Vectorization
- Similarity-based Content Filtering
- Singular Value Decomposition (SVD)
- Collaborative Filtering
- Hybrid Recommendation

### Backend

- Flask

### Frontend

- HTML5
- CSS3
- JavaScript

### Development Tools

- VS Code
- Git
- GitHub

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/adityavish02/smartbook.git
```

Move into the project directory:

```bash
cd smartbook
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Flask application

```bash
python app.py
```

The application will start at:

```text
http://127.0.0.1:5000
```

Open the URL in your browser.

## 🔌 API Endpoints

### Search Books

```text
GET /api/search?q=<query>
```

Example:

```text
/api/search?q=Harry%20Potter
```

Returns matching books.

### Generate Recommendations

```text
GET /api/recommend/<isbn>
```

Example:

```text
/api/recommend/059035342X
```

Returns:

- Selected book
- Recommended books
- Content similarity score
- Collaborative similarity score
- Hybrid score

### Get Book

```text
GET /api/book/<isbn>
```

Returns information about a specific book.

## 🔬 Machine Learning Pipeline

The project follows a modular machine learning pipeline.

```text
Raw Dataset
     ↓
Data Processing
     ↓
Cleaning & Transformation
     ↓
Feature Engineering
     ↓
       ┌──────────────────┐
       │                  │
       ▼                  ▼
  TF-IDF Pipeline     Rating Pipeline
       │                  │
       ▼                  ▼
Content Similarity       SVD
       │                  │
       └────────┬─────────┘
                ▼
        Hybrid Recommendation
                ↓
         Ranked Book List
```

## 📈 Recommendation Score

For every candidate book, SmartBook calculates three signals.

### Content Score

Measures similarity between the selected book and candidate book based on the content representation.

```text
Content Score ∈ [0, 1]
```

### Collaborative Score

Measures similarity derived from reader-rating patterns.

```text
Collaborative Score ∈ [0, 1]
```

### Hybrid Score

The two signals are combined:

```text
Hybrid Score =
    0.60 × Content Score
    +
    0.40 × Collaborative Score
```

The books are then ranked according to their hybrid scores.

## 🎯 Why Hybrid Recommendation?

A single recommendation strategy can have limitations.

### Content-Based Filtering

Can identify books that are similar in their characteristics, but may not fully capture what readers with similar preferences enjoy.

### Collaborative Filtering

Can capture reader behavior, but may have difficulty when rating information is limited.

### Hybrid Recommendation

SmartBook combines both approaches so that recommendations consider:

```text
Book Characteristics
        +
Reader Behavior
        ↓
Hybrid Recommendation
```

## 🧪 Example

Suppose a user selects:

```text
Harry Potter and the Sorcerer's Stone
```

SmartBook analyzes the selected book and generates candidate recommendations.

For a candidate book, suppose the model produces:

```text
Content Score        → 0.91
Collaborative Score  → 0.76
```

The hybrid score is calculated as:

```text
0.60 × 0.91 + 0.40 × 0.76
```

which gives approximately:

```text
0.85
```

Therefore:

```text
Hybrid Match ≈ 85%
```

The recommendation interface exposes the individual signals so users can understand how the final recommendation is produced.

## 📸 Application Preview

Add screenshots of the application here.

Create a `screenshots/` folder and place your screenshots inside it.

For example:

```markdown
![SmartBook Home](screenshots/home.png)

![SmartBook Recommendations](screenshots/recommendations.png)
```

## 🚧 Future Improvements

Potential improvements include:

- Personalized recommendations based on individual user profiles
- Cold-start handling for new users and books
- Advanced natural language embeddings
- Transformer-based semantic similarity
- Better recommendation evaluation metrics
- Precision@K
- Recall@K
- NDCG
- User authentication
- Personalized reading history
- Favorite/bookmark functionality
- Recommendation explanations using interpretable signals
- Model experimentation and hyperparameter tuning
- Cloud deployment
- API documentation
- Automated model retraining pipeline

## 📚 Learning Outcomes

This project demonstrates practical implementation of:

- Data preprocessing
- Feature engineering
- TF-IDF
- Similarity-based recommendation
- Collaborative filtering
- SVD
- Hybrid recommendation systems
- Machine learning pipelines
- Flask API development
- REST-style API endpoints
- Frontend-backend integration
- Model persistence
- Git and GitHub
- ML application architecture

## 👨‍💻 Author

**Aditya Vishwakarma**

B.Tech — Electronics and Communication Engineering  
National Institute of Technology, Agartala

## ⭐ Project

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.

## 📄 License

This project is intended for educational and portfolio purposes.
