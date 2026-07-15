from pathlib import Path
from datetime import datetime, timezone
import csv


BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_LOG_PATH = BASE_DIR / "data" / "audit_log.csv"


def save_review_to_audit_log(
    ticket_text,
    review_status,
    recommended_category,
    recommended_urgency,
    recommended_assignment_group,
    user_response,
    internal_work_note,
):
    """
    Save one human review decision to a CSV audit log.
    """

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ticket_text": ticket_text,
        "review_status": review_status,
        "recommended_category": recommended_category,
        "recommended_urgency": recommended_urgency,
        "recommended_assignment_group": recommended_assignment_group,
        "user_response": user_response,
        "internal_work_note": internal_work_note,
    }

    file_already_exists = AUDIT_LOG_PATH.exists()

    with open(
        AUDIT_LOG_PATH,
        mode="a",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=record.keys(),
        )

        if not file_already_exists:
            writer.writeheader()

        writer.writerow(record)