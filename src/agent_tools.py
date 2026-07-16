from load_tickets import load_tickets
from ticket_classifier import classify_ticket
from similar_ticket_search import find_similar_tickets
from knowledge_base_search import find_relevant_articles


def classify_ticket_tool(ticket_text):
    """
    Classify a support ticket and recommend its routing.
    """

    category, urgency, assignment_group = classify_ticket(
        ticket_text
    )

    return {
        "category": category,
        "urgency": urgency,
        "assignment_group": assignment_group,
    }


def search_similar_tickets_tool(ticket_text, top_n=1):
    """
    Search the historical ticket dataset for similar tickets.
    """

    tickets = load_tickets()

    matches = find_similar_tickets(
        ticket_text,
        tickets,
        top_n=top_n,
    )

    results = []

    for match in matches:
        results.append(
            {
                "ticket_id": match["ticket_id"],
                "ticket_text": match["ticket_text"],
                "category": match["category"],
                "urgency": match["urgency"],
                "assignment_group": match[
                    "assignment_group"
                ],
                "resolution": match["resolution"],
                "similarity_score": float(
                    match["similarity_score"]
                ),
            }
        )

    return results


def search_knowledge_base_tool(ticket_text, top_n=2):
    """
    Search the knowledge base for relevant articles.
    """

    articles = find_relevant_articles(
        ticket_text,
        top_n=top_n,
    )

    results = []

    for article in articles:
        results.append(
            {
                "article_id": article["article_id"],
                "title": article["title"],
                "category": article["category"],
                "content": article["content"],
                "similarity_score": float(
                    article["similarity_score"]
                ),
            }
        )

    return results