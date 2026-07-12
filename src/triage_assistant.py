from load_tickets import load_tickets
from similar_ticket_search import find_similar_tickets
from ticket_classifier import classify_ticket
from knowledge_base_search import find_relevant_articles
from response_generator import generate_user_response, generate_internal_work_note


MIN_SIMILARITY_SCORE = 0.25


def create_triage_suggestion(new_ticket_text):
    """
    Create a full ITSM copilot suggestion.
    """

    tickets = load_tickets()

    category, urgency, assignment_group = classify_ticket(new_ticket_text)

    similar_tickets = find_similar_tickets(new_ticket_text, tickets, top_n=1)
    best_match = similar_tickets[0]
    similarity_score = best_match["similarity_score"]

    relevant_articles = find_relevant_articles(new_ticket_text, top_n=2)

    if similarity_score >= MIN_SIMILARITY_SCORE:
        confidence_status = "High enough"
        action = "Suggest resolution"
        suggested_resolution = best_match["resolution"]
    else:
        confidence_status = "Low confidence"
        action = "Escalate to human support"
        suggested_resolution = (
            "No reliable past resolution found. "
            "A human support agent should review this ticket."
        )

    user_response = generate_user_response(
        new_ticket_text,
        category,
        assignment_group,
        suggested_resolution,
        confidence_status
    )

    internal_work_note = generate_internal_work_note(
        category,
        urgency,
        assignment_group,
        best_match["ticket_id"],
        similarity_score,
        suggested_resolution,
        relevant_articles,
        confidence_status,
        action
    )

    suggestion = {
        "new_ticket": new_ticket_text,
        "recommended_category": category,
        "recommended_urgency": urgency,
        "recommended_assignment_group": assignment_group,
        "similar_ticket_id": best_match["ticket_id"],
        "similar_ticket_text": best_match["ticket_text"],
        "similarity_score": similarity_score,
        "confidence_status": confidence_status,
        "recommended_action": action,
        "suggested_resolution": suggested_resolution,
        "relevant_articles": relevant_articles,
        "user_response": user_response,
        "internal_work_note": internal_work_note
    }

    return suggestion


if __name__ == "__main__":
    new_ticket = input("Enter new ticket: ")

    suggestion = create_triage_suggestion(new_ticket)

    print("\n--- AI ITSM Copilot Suggestion ---")
    print("New Ticket:", suggestion["new_ticket"])
    print("Recommended Category:", suggestion["recommended_category"])
    print("Recommended Urgency:", suggestion["recommended_urgency"])
    print("Recommended Assignment Group:", suggestion["recommended_assignment_group"])

    print("\nBased on Similar Past Ticket:")
    print("Ticket ID:", suggestion["similar_ticket_id"])
    print("Similarity Score:", round(suggestion["similarity_score"], 2))
    print("Confidence:", suggestion["confidence_status"])
    print("Similar Ticket:", suggestion["similar_ticket_text"])

    print("\nRecommended Action:")
    print(suggestion["recommended_action"])

    print("\nSuggested Resolution:")
    print(suggestion["suggested_resolution"])

    print("\nRelevant Knowledge Articles:")
    for article in suggestion["relevant_articles"]:
        print("\nArticle ID:", article["article_id"])
        print("Title:", article["title"])
        print("Category:", article["category"])
        print("Score:", round(article["similarity_score"], 2))

    print("\nDraft Response to User:")
    print(suggestion["user_response"])

    print("\nInternal Work Note:")
    print(suggestion["internal_work_note"])