import sqlite3

DB_NAME = "dailybrief.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        summary TEXT,
        link TEXT,
        published_date TEXT,
        category TEXT,
        image_url TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("Database ready")

def create_bookmarks_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        summary TEXT,
        link TEXT,
        category TEXT,
        image_url TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_news(
        title,
        summary,
        link,
        published_date,
        category,
        image_url
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO news
        (
            title,
            summary,
            link,
            published_date,
            category,
            image_url
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            summary,
            link,
            published_date,
            category,
            image_url
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()

def save_bookmark(
        title,
        summary,
        link,
        category,
        image_url
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bookmarks
    (
        title,
        summary,
        link,
        category,
        image_url
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        summary,
        link,
        category,
        image_url
    ))

    conn.commit()
    conn.close()

def remove_bookmark(bookmark_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bookmarks WHERE id=?",
        (bookmark_id,)
    )

    conn.commit()
    conn.close()

def news_exists(title):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM news WHERE title = ?",
        (title,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def view_news():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, summary, link, published_date, category, image_url
    FROM news
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def clear_news():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM news")

    conn.commit()
    conn.close()

    print("All news deleted")


def get_news_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM news")

    count = cursor.fetchone()[0]

    conn.close()

    return count


def search_news(keyword):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, summary, link, published_date, category, image_url
    FROM news
    WHERE title LIKE ?
    ORDER BY id DESC
    """, (f"%{keyword}%",))

    results = cursor.fetchall()

    conn.close()

    return results


def get_news_page(page, per_page=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    cursor.execute("""
    SELECT id, title, summary, link, published_date, category, image_url
    FROM news
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """, (per_page, offset))

    news = cursor.fetchall()

    conn.close()

    return news


def get_news_by_category(category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, summary, link, published_date, category, image_url
    FROM news
    WHERE category = ?
    ORDER BY id DESC
    """, (category,))

    news = cursor.fetchall()

    conn.close()

    return news


def get_categories():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT category
    FROM news
    ORDER BY category
    """)

    categories = [row[0] for row in cursor.fetchall()]

    conn.close()

    return categories


# =========================
# Dashboard Statistics
# =========================

def get_category_count(category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM news WHERE category = ?",
        (category,)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def get_stats():
    return {
        "total": get_news_count(),
        "technology": get_category_count("Technology"),
        "business": get_category_count("Business"),
        "politics": get_category_count("Politics"),
        "sports": get_category_count("Sports"),
        "general": get_category_count("General")
    }

def get_bookmarks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM bookmarks
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows







if __name__ == "__main__":
    news = view_news()

    for row in news:
        print(row[1], "=>", row[5])

    print(f"Categories: {get_categories()}")
    print(get_stats())
