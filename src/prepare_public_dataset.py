from pathlib import Path

import re

import pandas as pd

from ticket_classifier import classify_ticket


# Main project folder
project_root = Path(__file__).resolve().parents[1]

# Original downloaded dataset
raw_dataset_path = (
    project_root
    / "data"
    / "raw"
    / "public_support_tickets_raw.csv"
)

# Cleaned dataset that our project will use
processed_dataset_path = (
    project_root
    / "data"
    / "processed"
    / "public_support_tickets_processed.csv"
)

def clean_text(value):
    """
    Remove dataset formatting artefacts and placeholders.
    """

    text = str(value)

    # Convert written \n and real line breaks into spaces
    text = text.replace("\\n", " ")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")

    # Remove placeholders such as <tel_num> and <email_address>
    text = re.sub(r"<[^>]+>", "", text)

    # Replace repeated spaces with one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# Load the original dataset
df = pd.read_csv(raw_dataset_path)

print(f"Original rows: {len(df)}")


# Keep English tickets only
df = df[df["language"] == "en"].copy()

print(f"English rows: {len(df)}")


# Remove tickets missing essential information
df = df.dropna(
    subset=[
        "subject",
        "body",
        "answer",
        "priority",
        "queue",
        "type",
    ]
).copy()

print(f"Usable English rows: {len(df)}")


# Keep queues that are relevant to an IT service desk
allowed_queues = [
    "Technical Support",
    "IT Support",
    "Service Outages and Maintenance",
]

# Keep operational ITSM ticket types
allowed_types = [
    "Incident",
    "Problem",
]

df = df[
    df["queue"].isin(allowed_queues)
    & df["type"].isin(allowed_types)
].copy()

print(f"ITSM-filtered rows: {len(df)}")


# Combine the subject and body into one searchable ticket description
df["ticket_text"] = (
    df["subject"].apply(clean_text)
    + ". "
    + df["body"].apply(clean_text)
)


# Generate a category using our existing rule-based classifier
df["category"] = df["ticket_text"].apply(
    lambda text: classify_ticket(text)[0]
)


# Convert values such as "high" to "High"
df["urgency"] = (
    df["priority"]
    .astype(str)
    .str.strip()
    .str.title()
)


# Use the dataset queue as the historical assignment group
df["assignment_group"] = (
    df["queue"]
    .astype(str)
    .str.strip()
)


# Use the support answer as the historical resolution
df["resolution"] = df["answer"].apply(clean_text)


# Reset row numbers before generating ticket IDs
df = df.reset_index(drop=True)

df["ticket_id"] = [
    f"PUB{i:05d}"
    for i in range(1, len(df) + 1)
]


# Keep exactly the columns expected by our current project
processed_df = df[
    [
        "ticket_id",
        "ticket_text",
        "category",
        "urgency",
        "assignment_group",
        "resolution",
    ]
]


# Save the processed dataset
processed_df.to_csv(
    processed_dataset_path,
    index=False,
    encoding="utf-8",
)

print("\nProcessed dataset saved:")
print(processed_dataset_path)

print(f"\nProcessed rows: {len(processed_df)}")

print("\nCategory counts:")
print(processed_df["category"].value_counts())

print("\nUrgency counts:")
print(processed_df["urgency"].value_counts())

print("\nAssignment-group counts:")
print(processed_df["assignment_group"].value_counts())