// ============================================================
// SMARTBOOK - SINGLE PAGE RECOMMENDATION ENGINE
// ============================================================


// ============================================================
// DOM ELEMENTS
// ============================================================

const searchInput =
    document.getElementById("book-search");

const searchResults =
    document.getElementById("search-results");

const searchLoader =
    document.getElementById("search-loader");

const selectedSection =
    document.getElementById("selected-section");

const selectedBookContainer =
    document.getElementById("selected-book");

const recommendationSection =
    document.getElementById("recommendations-section");

const recommendationGrid =
    document.getElementById("recommendation-grid");

const recommendationLoading =
    document.getElementById("recommendation-loading");

const explanationSection =
    document.getElementById("explanation-section");

const emptyState =
    document.getElementById("empty-state");


// ============================================================
// STATE
// ============================================================

let searchTimeout = null;

let currentBook = null;


// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function formatRating(rating) {

    const value = Number(rating || 0);

    if (!value) {
        return "N/A";
    }

    return value.toFixed(2);
}


function formatNumber(number) {

    const value = Number(number || 0);

    return value.toLocaleString();
}


function scoreToPercent(score) {

    let value = Number(score || 0);

    /*
     * Recommendation scores are normally normalized between
     * 0 and 1.
     */

    if (value <= 1) {
        value *= 100;
    }

    value = Math.max(0, Math.min(100, value));

    return Math.round(value);
}


function getCover(book) {

    return (
        book.image_large ||
        book.image_medium ||
        book.image_small ||
        ""
    );
}


// ============================================================
// SEARCH
// ============================================================

searchInput.addEventListener("input", function () {

    const query =
        searchInput.value.trim();


    clearTimeout(searchTimeout);


    if (query.length < 2) {

        searchResults.innerHTML = "";

        searchResults.classList.remove("visible");

        searchLoader.classList.remove("active");

        return;
    }


    searchTimeout = setTimeout(
        () => performSearch(query),
        300
    );

});


async function performSearch(query) {

    searchLoader.classList.add("active");


    try {

        const response =
            await fetch(
                `/api/search?q=${encodeURIComponent(query)}`
            );


        if (!response.ok) {
            throw new Error("Search request failed");
        }


        const books =
            await response.json();


        renderSearchResults(books);


    } catch (error) {

        console.error(error);

        searchResults.innerHTML = `
            <div class="search-error">
                Unable to search books.
            </div>
        `;

        searchResults.classList.add("visible");

    } finally {

        searchLoader.classList.remove("active");

    }

}


// ============================================================
// SEARCH RESULTS
// ============================================================

function renderSearchResults(books) {

    if (!books || books.length === 0) {

        searchResults.innerHTML = `
            <div class="no-results">
                No matching books found.
            </div>
        `;

        searchResults.classList.add("visible");

        return;
    }


    searchResults.innerHTML =
        books.map(book => {

            const cover =
                getCover(book);


            return `

                <div
                    class="search-result"
                    data-isbn="${escapeHTML(book.isbn)}"
                >

                    <div class="search-result-cover">

                        ${
                            cover
                                ? `
                                    <img
                                        src="${escapeHTML(cover)}"
                                        alt=""
                                        loading="lazy"
                                    >
                                  `
                                : `
                                    <div class="cover-placeholder">
                                        📚
                                    </div>
                                  `
                        }

                    </div>


                    <div class="search-result-info">

                        <div class="search-result-title">

                            ${escapeHTML(book.title)}

                        </div>

                        <div class="search-result-author">

                            ${escapeHTML(book.author)}

                        </div>


                        <div class="search-result-meta">

                            <span>
                                ★ ${formatRating(book.rating)}
                            </span>

                            ${
                                book.rating_count
                                    ? `
                                        <span>
                                            ${formatNumber(
                                                book.rating_count
                                            )} ratings
                                        </span>
                                      `
                                    : ""
                            }

                        </div>

                    </div>

                </div>

            `;

        }).join("");


    searchResults.classList.add("visible");


    document
        .querySelectorAll(".search-result")
        .forEach(element => {

            element.addEventListener(
                "click",
                function () {

                    const isbn =
                        this.dataset.isbn;

                    selectBook(isbn);

                }
            );

        });

}


// ============================================================
// SELECT BOOK
// ============================================================

async function selectBook(isbn) {

    if (!isbn) {
        return;
    }


    searchResults.classList.remove("visible");

    searchResults.innerHTML = "";

    searchInput.value = "";


    // Hide empty state

    emptyState.classList.add("hidden");


    // Show loading

    selectedSection.classList.remove("hidden");

    recommendationSection.classList.add("hidden");

    explanationSection.classList.add("hidden");

    recommendationLoading.classList.remove("hidden");


    // Scroll to selected book

    selectedSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });


    try {

        const response =
            await fetch(
                `/api/recommend/${encodeURIComponent(isbn)}`
            );


        if (!response.ok) {

            const errorData =
                await response.json();

            throw new Error(
                errorData.error ||
                "Recommendation request failed"
            );

        }


        const data =
            await response.json();


        currentBook =
            data.book;


        renderSelectedBook(
            data.book
        );


        renderRecommendations(
            data.recommendations
        );


        recommendationLoading.classList.add(
            "hidden"
        );

        recommendationSection.classList.remove(
            "hidden"
        );

        explanationSection.classList.remove(
            "hidden"
        );


        setTimeout(() => {

            recommendationSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 150);


    } catch (error) {

        console.error(error);


        recommendationLoading.classList.add(
            "hidden"
        );


        selectedBookContainer.innerHTML = `

            <div class="error-card">

                <div class="error-icon">
                    ⚠
                </div>

                <div>

                    <h3>
                        Something went wrong
                    </h3>

                    <p>
                        ${escapeHTML(error.message)}
                    </p>

                </div>

            </div>

        `;

    }

}


// ============================================================
// SELECTED BOOK
// ============================================================

function renderSelectedBook(book) {

    const cover =
        getCover(book);


    selectedBookContainer.innerHTML = `

        <div class="selected-cover">

            ${
                cover
                    ? `
                        <img
                            src="${escapeHTML(cover)}"
                            alt="${escapeHTML(book.title)}"
                        >
                      `
                    : `
                        <div class="large-cover-placeholder">
                            📚
                        </div>
                      `
            }

        </div>


        <div class="selected-info">

            <div class="selected-tag">
                SELECTED BOOK
            </div>


            <h2>

                ${escapeHTML(book.title)}

            </h2>


            <p class="selected-author">

                ${escapeHTML(book.author)}

            </p>


            <div class="selected-meta">

                <div class="rating">

                    <span class="star">
                        ★
                    </span>

                    <strong>
                        ${formatRating(book.rating)}
                    </strong>

                </div>


                ${
                    book.rating_count
                        ? `
                            <div class="rating-count">

                                ${formatNumber(
                                    book.rating_count
                                )}
                                reader ratings

                            </div>
                          `
                        : ""
                }

            </div>

        </div>


        <div class="selected-action">

            <div class="ai-symbol">
                ✦
            </div>

            <span>
                Analyzing
            </span>

            <small>
                Content + readers
            </small>

        </div>

    `;

}


// ============================================================
// RECOMMENDATIONS
// ============================================================

function renderRecommendations(books) {

    if (!books || books.length === 0) {

        recommendationGrid.innerHTML = `

            <div class="no-recommendations">

                <div>
                    📚
                </div>

                <h3>
                    No recommendations found
                </h3>

                <p>
                    Try selecting another book.
                </p>

            </div>

        `;

        return;
    }


    recommendationGrid.innerHTML =
        books.map((book, index) => {

            const cover =
                getCover(book);


            const hybrid =
                scoreToPercent(
                    book.hybrid_score
                );


            const content =
                scoreToPercent(
                    book.content_score
                );


            const collaborative =
                scoreToPercent(
                    book.collaborative_score
                );


            return `

                <article
                    class="book-card"
                    data-isbn="${escapeHTML(book.isbn)}"
                >


                    <!-- RANK -->

                    <div class="book-rank">

                        ${String(index + 1).padStart(2, "0")}

                    </div>


                    <!-- COVER -->

                    <div class="book-cover">

                        ${
                            cover
                                ? `
                                    <img
                                        src="${escapeHTML(cover)}"
                                        alt="${escapeHTML(book.title)}"
                                        loading="lazy"
                                    >
                                  `
                                : `
                                    <div class="cover-placeholder large">
                                        📚
                                    </div>
                                  `
                        }

                        <div class="hybrid-badge">

                            ${hybrid}%

                            <span>
                                match
                            </span>

                        </div>

                    </div>


                    <!-- INFORMATION -->

                    <div class="book-card-body">


                        <h3 class="book-title">

                            ${escapeHTML(book.title)}

                        </h3>


                        <p class="book-author">

                            ${escapeHTML(book.author)}

                        </p>


                        <div class="book-rating">

                            <span>
                                ★
                            </span>

                            ${formatRating(book.rating)}

                            ${
                                book.rating_count
                                    ? `
                                        <small>
                                            ·
                                            ${formatNumber(
                                                book.rating_count
                                            )}
                                        </small>
                                      `
                                    : ""
                            }

                        </div>


                        <!-- SCORE BREAKDOWN -->

                        <div class="score-section">

                            <div class="score-row">

                                <div class="score-label">

                                    <span>
                                        Content
                                    </span>

                                    <strong>
                                        ${content}%
                                    </strong>

                                </div>


                                <div class="score-bar">

                                    <div
                                        class="score-fill content-score"
                                        style="width: ${content}%"
                                    ></div>

                                </div>

                            </div>


                            <div class="score-row">

                                <div class="score-label">

                                    <span>
                                        Readers
                                    </span>

                                    <strong>
                                        ${collaborative}%
                                    </strong>

                                </div>


                                <div class="score-bar">

                                    <div
                                        class="score-fill reader-score"
                                        style="width: ${collaborative}%"
                                    ></div>

                                </div>

                            </div>


                        </div>


                        <div class="view-recommendation">

                            Explore this book

                            <span>
                                →
                            </span>

                        </div>


                    </div>

                </article>

            `;

        }).join("");


    // Clicking a recommendation makes it the
    // new input book.

    document
        .querySelectorAll(".book-card")
        .forEach(card => {

            card.addEventListener(
                "click",
                function () {

                    const isbn =
                        this.dataset.isbn;

                    selectBook(isbn);

                }
            );

        });

}


// ============================================================
// CLICK OUTSIDE SEARCH
// ============================================================

document.addEventListener(
    "click",
    function (event) {

        if (
            !event.target.closest(
                ".search-wrapper"
            )
        ) {

            searchResults.classList.remove(
                "visible"
            );

        }

    }
);


// ============================================================
// KEYBOARD SHORTCUT
// ============================================================

searchInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            searchResults.classList.remove(
                "visible"
            );

            searchInput.blur();

        }

    }
);