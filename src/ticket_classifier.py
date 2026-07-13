def contains_any(text, keywords):
    """
    Return True when at least one keyword appears in the ticket text.
    """
    return any(keyword in text for keyword in keywords)


def classify_ticket(ticket_text):
    """
    Rule-based IT service-ticket classifier.

    It recommends:
    - category
    - urgency
    - assignment group
    """

    text = ticket_text.lower()

    if contains_any(
        text,
        [
            "service outage",
            "system outage",
            "downtime",
            "service disruption",
            "system interruption",
            "service interruption",
            "system unavailable",
            "service unavailable",
            "widespread disruption",
        ],
    ):
        category = "Service Outage"
        urgency = "High"
        assignment_group = "Service Operations"

    elif contains_any(
        text,
        [
            "vpn",
            "wifi",
            "wi-fi",
            "network",
            "router",
            "internet",
            "ethernet",
            "dns",
            "ip address",
            "latency",
        ],
    ):
        category = "Network"
        urgency = "Medium"
        assignment_group = "Network Support"

    elif contains_any(
        text,
        [
            "email",
            "outlook",
            "mailbox",
            "smtp",
            "imap",
        ],
    ):
        category = "Email"
        urgency = "Low"
        assignment_group = "Messaging Support"

    elif contains_any(
        text,
        [
            "password",
            "login",
            "log in",
            "sign in",
            "account locked",
            "locked account",
            "access denied",
            "authentication",
            "mfa",
            "multi-factor",
        ],
    ):
        category = "Access"
        urgency = "Low"
        assignment_group = "IT Helpdesk"

    elif contains_any(
        text,
        [
            "laptop",
            "screen",
            "keyboard",
            "printer",
            "monitor",
            "headset",
            "usb",
            "peripheral",
            "hard drive",
            "storage device",
            "overheating",
        ],
    ):
        category = "Hardware"
        urgency = "Medium"
        assignment_group = "Hardware Support"

    elif contains_any(
        text,
        [
            "software",
            "application",
            "app",
            "saas",
            "crash",
            "integration",
            "dashboard",
            "database",
            "postgresql",
            "elasticsearch",
            "gimp",
            "upgrade",
            "installation",
        ],
    ):
        category = "Software"
        urgency = "Medium"
        assignment_group = "Application Support"

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