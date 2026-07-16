from pathlib import Path
from datetime import datetime, timezone
import csv
import json


BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_LOG_PATH = BASE_DIR / "data" / "audit_log.csv"
AGENT_AUDIT_LOG_PATH = BASE_DIR / "data" / "agent_audit_log.csv"


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
def save_agent_review_to_audit_log(
    ticket_text,
    review_status,
    agent_response,
    tool_trace,
):
    """
    Save one human review decision for the agent workflow.
    """

    tools_used = [
        step.get("tool_name", "")
        for step in tool_trace
    ]

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ticket_text": ticket_text,
        "review_status": review_status,
        "agent_response": agent_response,
        "tools_used": ", ".join(tools_used),
        "tool_trace_json": json.dumps(
            tool_trace,
            ensure_ascii=False,
        ),
    }

    file_already_exists = AGENT_AUDIT_LOG_PATH.exists()

    with open(
        AGENT_AUDIT_LOG_PATH,
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