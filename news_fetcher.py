import feedparser


def fetch_news():
    rss_url = "https://www.thehindu.com/news/feeder/default.rss"

    feed = feedparser.parse(rss_url)

    articles = []

    for entry in feed.entries[:10]:

        image_url = ""

        try:
            if "media_content" in entry:
                image_url = entry.media_content[0]["url"]
        except Exception:
            image_url = ""

        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "N/A"),
            "description": entry.get("summary", ""),
            "image_url": image_url
        })

    return articles


if __name__ == "__main__":

    articles = fetch_news()

    print("\nTOTAL ARTICLES:", len(articles))

    if articles:
        print("\nFIRST ARTICLE:\n")
        print(articles[0])
