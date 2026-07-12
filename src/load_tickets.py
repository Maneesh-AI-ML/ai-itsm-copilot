from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "sample_tickets.csv"


def load_tickets():
    """
    Load support tickets from the CSV file.
    Each ticket becomes a Python dictionary.
    """

    tickets = []

    with open(DATA_PATH, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tickets.append(row)

    return tickets


if __name__ == "__main__":
    tickets = load_tickets()

    print(f"Loaded {len(tickets)} tickets\n")

    for ticket in tickets:
        print(
            ticket["ticket_id"],
            "-",
            ticket["category"],
            "-",
            ticket["ticket_text"]
        )