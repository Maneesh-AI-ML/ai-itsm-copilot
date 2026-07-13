from load_tickets import load_tickets

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(text1, text2):
    """
    Compare two texts using TF-IDF and cosine similarity.
    This is better than simple word overlap.
    """

    documents = [text1, text2]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_score = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return similarity_score


def find_similar_tickets(new_ticket_text, tickets, top_n=3):
    """
    Find the most similar old tickets using TF-IDF similarity.
    """

    ticket_texts = [ticket["ticket_text"] for ticket in tickets]

    documents = [new_ticket_text] + ticket_texts

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    new_ticket_vector = tfidf_matrix[0:1]
    old_ticket_vectors = tfidf_matrix[1:]

    similarity_scores = cosine_similarity(
        new_ticket_vector,
        old_ticket_vectors
    )[0]

    results = []

    for ticket, score in zip(tickets, similarity_scores):
        results.append({
            "ticket_id": ticket["ticket_id"],
            "ticket_text": ticket["ticket_text"],
            "category": ticket["category"],
            "urgency": ticket["urgency"],
            "assignment_group": ticket["assignment_group"],
            "resolution": ticket["resolution"],
            "similarity_score": score
        })

    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)

    return results[:top_n]


if __name__ == "__main__":
    tickets = load_tickets()

    new_ticket = input("Enter new ticket: ")

    similar_tickets = find_similar_tickets(new_ticket, tickets)

    print("\n--- Similar Past Tickets ---")

    for ticket in similar_tickets:
        print("\nTicket ID:", ticket["ticket_id"])
        print("Score:", round(ticket["similarity_score"], 2))
        print("Old Ticket:", ticket["ticket_text"])
        print("Category:", ticket["category"])
        print("Urgency:", ticket["urgency"])
        print("Assignment Group:", ticket["assignment_group"])
        print("Past Resolution:", ticket["resolution"])