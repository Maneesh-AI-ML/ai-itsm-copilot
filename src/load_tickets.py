from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parent.parent

PUBLIC_DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "public_support_tickets_processed.csv"
)

SAMPLE_DATA_PATH = BASE_DIR / "data" / "sample_tickets.csv"


def load_tickets():
    """
    Load historical support tickets from a CSV file.

    The processed public dataset is used when available.
    The small sample dataset is kept as a fallback.
    """

    if PUBLIC_DATA_PATH.exists():
        data_path = PUBLIC_DATA_PATH
    else:
        data_path = SAMPLE_DATA_PATH

    tickets = []

    with open(
        data_path,
        mode="r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            tickets.append(row)

    print(f"Loaded dataset: {data_path.name}")

    return tickets


if __name__ == "__main__":
    tickets = load_tickets()

    print(f"Loaded {len(tickets)} tickets\n")

    for ticket in tickets[:5]:
        print(
            ticket["ticket_id"],
            "-",
            ticket["category"],
            "-",
            ticket["ticket_text"][:100],
        )