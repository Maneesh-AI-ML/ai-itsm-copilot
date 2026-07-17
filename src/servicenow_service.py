import os

import requests
from dotenv import load_dotenv


load_dotenv()


SERVICENOW_INSTANCE_URL = os.getenv(
    "SERVICENOW_INSTANCE_URL",
    "",
).rstrip("/")

SERVICENOW_USERNAME = os.getenv(
    "SERVICENOW_USERNAME",
    "",
)

SERVICENOW_PASSWORD = os.getenv(
    "SERVICENOW_PASSWORD",
    "",
)


def get_incident_by_number(incident_number):
    """
    Load one incident from ServiceNow using the Table API.
    """

    if not all(
        [
            SERVICENOW_INSTANCE_URL,
            SERVICENOW_USERNAME,
            SERVICENOW_PASSWORD,
        ]
    ):
        raise RuntimeError(
            "ServiceNow configuration is missing from .env."
        )

    url = (
        f"{SERVICENOW_INSTANCE_URL}"
        "/api/now/v1/table/incident"
    )

    params = {
        "sysparm_query": f"number={incident_number}",
        "sysparm_display_value": "true",
        "sysparm_limit": "1",
        "sysparm_fields": (
            "sys_id,number,short_description,description,"
            "state,category,impact,urgency,priority,"
            "assignment_group,work_notes"
        ),
    }

    response = requests.get(
        url,
        auth=(
            SERVICENOW_USERNAME,
            SERVICENOW_PASSWORD,
        ),
        headers={
            "Accept": "application/json",
        },
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    records = response.json().get("result", [])

    if not records:
        return None

    return records[0]


def add_work_note_to_incident(
    incident_sys_id,
    work_note,
):
    """
    Add an approved work note to a ServiceNow incident.
    """

    if not all(
        [
            SERVICENOW_INSTANCE_URL,
            SERVICENOW_USERNAME,
            SERVICENOW_PASSWORD,
        ]
    ):
        raise RuntimeError(
            "ServiceNow configuration is missing from .env."
        )

    if not incident_sys_id:
        raise ValueError(
            "ServiceNow incident sys_id is missing."
        )

    if not work_note.strip():
        raise ValueError(
            "Work note cannot be empty."
        )

    url = (
        f"{SERVICENOW_INSTANCE_URL}"
        f"/api/now/v1/table/incident/{incident_sys_id}"
    )

    response = requests.patch(
        url,
        auth=(
            SERVICENOW_USERNAME,
            SERVICENOW_PASSWORD,
        ),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "work_notes": work_note,
        },
        timeout=20,
    )

    response.raise_for_status()

    return response.json().get("result", {})

if __name__ == "__main__":
    incident = get_incident_by_number("INC0010010")

    if incident is None:
        print("Incident not found.")
    else:
        print("Incident loaded successfully.")
        print("Number:", incident.get("number"))
        print(
            "Short description:",
            incident.get("short_description"),
        )
        print("State:", incident.get("state"))
        print(
            "Assignment group:",
            incident.get("assignment_group"),
        )