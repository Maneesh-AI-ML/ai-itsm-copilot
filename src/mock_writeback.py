from pathlib import Path
from datetime import datetime, timezone
import csv


BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_WRITEBACK_PATH = BASE_DIR / "data" / "mock_writeback.csv"


def save_mock_writeback(
    ticket_text,
    review_status,
    agent_response,
):
    """
    Save an approved agent recommendation locally.

    This temporary local file will later be replaced by
    ServiceNow work_notes REST API write-back.
    """

    if review_status != "Approved":
        return {
            "success": False,
            "message": "Write-back blocked: the agent result is not approved.",
        }

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ticket_text": ticket_text,
        "review_status": review_status,
        "approved_agent_response": agent_response,
    }

    file_already_exists = MOCK_WRITEBACK_PATH.exists()

    with open(
        MOCK_WRITEBACK_PATH,
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

    return {
        "success": True,
        "message": "Approved agent result saved to mock write-back.",
    }