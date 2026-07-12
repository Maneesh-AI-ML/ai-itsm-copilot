from pathlib import Path
import csv

from similar_ticket_search import calculate_similarity


BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "data" / "knowledge_base.csv"


def load_knowledge_base():
    """
    Load knowledge base articles from CSV.
    Each article becomes a Python dictionary.
    """

    articles = []

    with open(KB_PATH, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            articles.append(row)

    return articles


def find_relevant_articles(ticket_text, top_n=2):
    """
    Find knowledge base articles most relevant to the new ticket.
    """

    articles = load_knowledge_base()
    results = []

    for article in articles:
        searchable_text = article["title"] + " " + article["content"]
        score = calculate_similarity(ticket_text, searchable_text)

        results.append({
            "article_id": article["article_id"],
            "title": article["title"],
            "category": article["category"],
            "content": article["content"],
            "similarity_score": score
        })

    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)

    return results[:top_n]


if __name__ == "__main__":
    new_ticket = input("Enter ticket: ")

    articles = find_relevant_articles(new_ticket)

    print("\n--- Relevant Knowledge Articles ---")

    for article in articles:
        print("\nArticle ID:", article["article_id"])
        print("Title:", article["title"])
        print("Category:", article["category"])
        print("Score:", round(article["similarity_score"], 2))
        print("Content:", article["content"])