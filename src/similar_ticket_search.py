import string
from load_tickets import load_tickets


STOP_WORDS = {
    "i", "am", "is", "are", "the", "a", "an", "to", "and", "or",
    "after", "before", "my", "me", "in", "on", "for", "with",
    "cannot", "can", "not", "this", "that"
}


def clean_text(text):
    """
    Convert text into useful words.
    Example:
    'I cannot connect to VPN after changing my password'
    becomes:
    {'connect', 'vpn', 'changing', 'password'}
    """

    text = text.lower()

    # Remove punctuation like . , ! ?
    text = text.translate(str.maketrans("", "", string.punctuation))

    words = text.split()

    useful_words = set()

    for word in words:
        if word not in STOP_WORDS:
            useful_words.add(word)

    return useful_words


def calculate_similarity(text1, text2):
    """
    Compare two texts using shared words.
    More shared useful words = more similar.
    """

    words1 = clean_text(text1)
    words2 = clean_text(text2)

    if not words1 or not words2:
        return 0

    common_words = words1.intersection(words2)
    all_words = words1.union(words2)

    similarity_score = len(common_words) / len(all_words)

    return similarity_score


def find_similar_tickets(new_ticket_text, tickets, top_n=3):
    """
    Find the most similar old tickets.
    """

    results = []

    for ticket in tickets:
        score = calculate_similarity(new_ticket_text, ticket["ticket_text"])

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