import time
from news_fetcher import fetch_news
from database import create_database, save_news, news_exists
from google import genai
from gemini_config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def summarize_news(text):

    max_retries = 3

    for attempt in range(max_retries):

        try:
            time.sleep(1)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
                You are a professional news editor.

                Create a clear and factual summary.

                Rules:
                - Use exactly 2 sentences.
                - Keep it under 60 words.
                - Mention the most important event.
                - Do not add opinions.
                - Use simple English.

                Article:
                {text}
                """
            )

            return response.text.strip()

        except Exception as e:

            print(
                f"Gemini Attempt {attempt + 1} Failed:",
                e
            )

            time.sleep(10)

    print("Using fallback summary")

    return text[:200]


def detect_category(title):

    title_lower = title.lower()

    if any(word in title_lower for word in [
        "cricket", "football", "tennis", "sports",
        "match", "tournament", "ipl", "olympics",
        "athlete", "championship"
    ]):
        return "Sports"

    elif any(word in title_lower for word in [
        "election", "government", "minister",
        "parliament", "assembly", "court",
        "supreme court", "high court",
        "mla", "mp", "rajya sabha",
        "lok sabha", "bjp", "congress",
        "policy", "polls"
    ]):
        return "Politics"

    elif any(word in title_lower for word in [
        "stock", "market", "business",
        "economy", "finance", "bank",
        "investment", "trade", "company",
        "industry"
    ]):
        return "Business"

    elif any(word in title_lower for word in [
        "technology", "tech", "software",
        "digital", "startup", "internet",
        "cyber", "robot",
        "artificial intelligence",
        "machine learning",
        "chatgpt", "gemini", "openai"
    ]):
        return "Technology"

    return "General"


def classify_category(title, description):

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
            Classify the following news article into ONLY ONE category.

            Categories:
            Technology
            Business
            Politics
            Sports
            General

            Return only the category name.

            Title:
            {title}

            Description:
            {description}
            """
        )

        category = response.text.strip()

        valid_categories = [
            "Technology",
            "Business",
            "Politics",
            "Sports",
            "General"
        ]

        if category in valid_categories:
            return category

    except Exception as e:
        print("Category Classification Error:", e)

    return detect_category(title)


def process_news():

    print("\nPROCESSING NEWS...\n")

    create_database()

    news_list = fetch_news()

    print(f"Articles fetched: {len(news_list)}\n")

    for article in news_list:

        title = article["title"]
        link = article["link"]
        published_date = article["published"]
        description = article["description"]
        image_url = article.get("image_url", "")

        if news_exists(title):
            print(f"Skipped duplicate: {title}")
            continue

        if description:
            summary = summarize_news(description)
        else:
            summary = title

        category = classify_category(
            title,
            description
        )

        saved = save_news(
            title,
            summary,
            link,
            published_date,
            category,
            image_url
        )

        if saved:
            print(f"Inserted: {title} [{category}]")
        else:
            print(f"Skipped duplicate: {title}")

    print("\nAll news processed successfully!")


if __name__ == "__main__":
    process_news()
