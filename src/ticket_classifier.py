def classify_ticket(ticket_text):
    """
    Basic rule-based ticket classifier.
    This is our first simple triage logic.
    """

    text = ticket_text.lower()

    if "vpn" in text or "network" in text or "wifi" in text:
        category = "Network"
        urgency = "Medium"
        assignment_group = "Network Support"

    elif "password" in text or "login" in text or "access" in text:
        category = "Access"
        urgency = "Low"
        assignment_group = "IT Helpdesk"

    elif "laptop" in text or "screen" in text or "keyboard" in text:
        category = "Hardware"
        urgency = "Medium"
        assignment_group = "Hardware Support"

    elif "email" in text or "outlook" in text:
        category = "Email"
        urgency = "Low"
        assignment_group = "Messaging Support"

    else:
        category = "General"
        urgency = "Low"
        assignment_group = "IT Helpdesk"

    return category, urgency, assignment_group


if __name__ == "__main__":
    ticket = input("Enter your ticket: ")

    category, urgency, assignment_group = classify_ticket(ticket)

    print("\n--- Basic Ticket Classification ---")
    print("Ticket:", ticket)
    print("Category:", category)
    print("Urgency:", urgency)
    print("Assignment Group:", assignment_group)