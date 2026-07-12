from flask import Flask, render_template, redirect, request, send_file
from datetime import datetime
from reportlab.pdfgen import canvas
import random


from database import (
    create_database,
    create_bookmarks_table,
    search_news,
    get_news_page,
    get_news_count,
    get_news_by_category,
    get_categories,
    get_stats,
    save_bookmark,
    get_bookmarks,
    view_news,
    remove_bookmark
)
from ai_summarizer import process_news

app = Flask(__name__)

create_database()
create_bookmarks_table()


@app.route("/")
def home():

    query = request.args.get("search")
    category = request.args.get("category")
    page = request.args.get("page", 1, type=int)

    if query:
        news = search_news(query)
        total_pages = 1

    elif category and category != "All":
        news = get_news_by_category(category)
        total_pages = 1

    else:
        news = get_news_page(page)

        total_news = get_news_count()
        total_pages = (total_news + 9) // 10

    stats = get_stats()

    return render_template(
        "index.html",
        news=news,
        query=query,
        page=page,
        total_pages=total_pages,
        selected_category=category,
        categories=get_categories(),
        stats=stats,
        last_updated=datetime.now().strftime(
            "%d %b %Y %I:%M %p"
        )
    )


@app.route("/refresh")
def refresh():
    process_news()
    return redirect("/")

@app.route("/remove_bookmark/<int:bookmark_id>")
def remove_bookmark_route(bookmark_id):
    remove_bookmark(bookmark_id)
    return redirect("/bookmarks")



@app.route("/bookmarks")
def bookmarks():

    bookmarks = get_bookmarks()

    return render_template(
        "bookmarks.html",
        bookmarks=bookmarks
    )

@app.route("/bookmark/<int:news_id>")
def bookmark(news_id):

    news = view_news()

    for article in news:

        if article[0] == news_id:

            save_bookmark(
                article[1],  # title
                article[2],  # summary
                article[3],  # link
                article[5],  # category
                article[6]   # image_url
            )

            break

    return redirect("/")

@app.route("/download_pdf")
def download_pdf():

    news = view_news()

    pdf_file = "dailybrief_news.pdf"

    c = canvas.Canvas(pdf_file)

    y = 800

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "DailyBriefAI News Report")

    y -= 40

    for article in news[:20]:

        title = article[1]
        summary = article[2]

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, title[:80])

        y -= 20

        c.setFont("Helvetica", 9)

        summary_lines = summary[:200]

        c.drawString(60, y, summary_lines)

        y -= 40

        if y < 100:
            c.showPage()
            y = 800

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )

@app.route("/monthly_magazine")
def monthly_magazine():

    news = view_news()

    pdf_file = "Monthly_Current_Affairs_Magazine.pdf"

    c = canvas.Canvas(pdf_file)
    # Cover Page

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(
        300,
        750,
        "DailyBriefAI"
    )

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(
        300,
        700,
        "Monthly Current Affairs Magazine"
    )

    c.setFont("Helvetica", 14)
    c.drawCentredString(
        300,
        650,
        datetime.now().strftime("%B %Y Edition")
    )

    c.setFont("Helvetica", 12)
    c.drawCentredString(
        300,
        600,
        f"Total Articles: {len(news)}"
    )

    c.drawCentredString(
        300,
        560,
        "Powered by AI & RSS News"
    )

    c.showPage()

    # Table of Contents

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "Table of Contents")

    c.setFont("Helvetica", 14)

    c.drawString(80, 680, "1. Politics")
    c.drawString(80, 650, "2. Business")
    c.drawString(80, 620, "3. Technology")
    c.drawString(80, 590, "4. Sports")
    c.drawString(80, 560, "5. General")

    c.showPage()


    # Start new page
    c.showPage()

    y = 800

    c.setFont("Helvetica-Bold", 18)
    c.drawString(
        50,
        y,
        "DailyBriefAI Monthly Current Affairs Magazine"
    )

    y -= 40

    categories = [
    "Politics",
    "Business",
    "Technology",
    "Sports",
    "General"
    ]

    for current_category in categories:

        category_news = [
            article
            for article in news
            if article[5] == current_category
        ]

        if not category_news:
            continue

        # Category Title

        c.setFont("Helvetica-Bold", 16)

        c.drawString(
            50,
            y,
            current_category.upper()
        )

        y -= 25

        for article in category_news[:10]:

            title = article[1]
            summary = article[2]

            c.setFont("Helvetica-Bold", 11)

            c.drawString(
                50,
                y,
                title[:80]
            )

            y -= 18


            c.setFont("Helvetica", 9)
            c.drawString(
                60,
                y,
                summary[:150]
            )

            y -= 35

            if y < 100:
                c.showPage()
                y = 800

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )

@app.route("/weekly_revision")
def weekly_revision():

    news = view_news()

    return render_template(
        "weekly_revision.html",
        news=news[:30]
    )

@app.route("/upsc_notes")
def upsc_notes():

    news = view_news()[:20]

    return render_template(
        "upsc_notes.html",
        news=news
    )

@app.route("/catchup")
def catchup():

    news = view_news()[:20]

    categories = {}

    for article in news:

        category = article[5]

        if category in categories:
            categories[category] += 1
        else:
            categories[category] = 1

    top_topics = sorted(
        categories.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return render_template(
        "catchup.html",
        news=news,
        topics=top_topics
    )

@app.route("/download_upsc_notes_pdf")
def download_upsc_notes_pdf():

    news = view_news()[:20]

    pdf_file = "DailyBriefAI_UPSC_Notes.pdf"

    c = canvas.Canvas(pdf_file)

    y = 800

    c.setFont("Helvetica-Bold", 18)
    c.drawString(
        50,
        y,
        "DailyBriefAI UPSC Current Affairs Notes"
    )

    y -= 40

    for article in news:

        title = article[1]
        summary = article[2]
        category = article[5]

        c.setFont("Helvetica-Bold", 11)
        c.drawString(
            50,
            y,
            title[:80]
        )

        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(
            60,
            y,
            f"Category: {category}"
        )

        y -= 20

        c.drawString(
            60,
            y,
            summary[:120]
        )

        y -= 40

        if y < 100:
            c.showPage()
            y = 800

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )

@app.route("/mcqs")
def mcqs():

    news = view_news()[:10]

    mcq_data = []

    organizations = [
        "RBI",
        "WHO",
        "IMF",
        "World Bank",
        "NITI Aayog",
        "UNESCO",
        "ISRO",
        "SEBI",
        "UPSC",
        "DRDO"
    ]

    for article in news:

        correct = random.choice(organizations)

        options = random.sample(
            organizations,
            4
        )

        if correct not in options:
            options[0] = correct

        random.shuffle(options)

        mcq_data.append({
            "question":
                "Which organization is most closely related to this news?",
            "title":
                article[1],
            "options":
                options,
            "answer":
                correct,
            "summary":
                article[2]
        })

    return render_template(
        "mcqs.html",
        mcqs=mcq_data
    )

@app.route("/download_mcq_pdf")
def download_mcq_pdf():

    news = view_news()[:10]

    pdf_file = "DailyBriefAI_MCQs.pdf"

    c = canvas.Canvas(pdf_file)

    y = 800

    c.setFont("Helvetica-Bold", 16)
    c.drawString(
        50,
        y,
        "DailyBriefAI Current Affairs MCQs"
    )

    y -= 40

    for i, article in enumerate(news, start=1):

        c.setFont("Helvetica-Bold", 11)

        c.drawString(
            50,
            y,
            f"Q{i}. {article[1][:70]}"
        )

        y -= 20

        c.setFont("Helvetica", 10)

        c.drawString(
            70,
            y,
            f"Answer: {article[5]}"
        )

        y -= 30

        if y < 100:
            c.showPage()
            y = 800

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    news = random.sample(view_news(), min(10, len(view_news())))

    score = None

    if request.method == "POST":

        score = 0

        for i, article in enumerate(news, start=1):

            user_answer = request.form.get(f"q{i}")

            if user_answer == article[5]:
                score += 1

    return render_template(
        "quiz.html",
        news=news,
        score=score
    )

@app.route("/test")
def test():
    return "TEST WORKING"

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    answer = None

    if request.method == "POST":

        question = request.form.get("question", "").lower()

        news = view_news()

        matching_news = []

        for article in news:

            title = article[1]
            summary = article[2]
            category = article[5]

            if (
                question in title.lower()
                or question in summary.lower()
                or question in category.lower()
            ):
                matching_news.append(
                    f"{title} - {summary}"
                )

        if matching_news:

            answer = "\n\n".join(
                matching_news[:5]
            )

        else:

            answer = (
                "No related news found."
            )

    return render_template(
        "chatbot.html",
        answer=answer
    )

if __name__ == "__main__":
    app.run(debug=True)
