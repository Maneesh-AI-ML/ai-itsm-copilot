import sys
from pathlib import Path

import streamlit as st


# Allow this app file to import code from the src folder
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from triage_assistant import create_triage_suggestion


st.set_page_config(
    page_title="AI ITSM Copilot",
    page_icon="🛠️",
    layout="wide"
)

st.title("AI ITSM Copilot")
st.write(
    "ServiceNow-style incident triage assistant for category, urgency, "
    "assignment group, similar tickets, knowledge articles, and support notes."
)

ticket_text = st.text_area(
    "Enter a new support ticket",
    placeholder="Example: VPN not working after password reset",
    height=120
)

analyze_button = st.button("Analyze Ticket")

if analyze_button:
    if not ticket_text.strip():
        st.warning("Please enter a ticket description.")
    else:
        suggestion = create_triage_suggestion(ticket_text)

        st.subheader("Triage Recommendation")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Category", suggestion["recommended_category"])

        with col2:
            st.metric("Urgency", suggestion["recommended_urgency"])

        with col3:
            st.metric("Assignment Group", suggestion["recommended_assignment_group"])

        st.subheader("Similar Past Ticket")
        st.write(f"**Ticket ID:** {suggestion['similar_ticket_id']}")
        st.write(f"**Similarity Score:** {round(suggestion['similarity_score'], 2)}")
        st.write(f"**Confidence:** {suggestion['confidence_status']}")
        st.write(f"**Similar Ticket:** {suggestion['similar_ticket_text']}")

        st.subheader("Recommended Action")
        st.info(suggestion["recommended_action"])

        st.subheader("Suggested Resolution")
        st.write(suggestion["suggested_resolution"])

        st.subheader("Relevant Knowledge Articles")

        for article in suggestion["relevant_articles"]:
            with st.expander(f"{article['article_id']} - {article['title']}"):
                st.write(f"**Category:** {article['category']}")
                st.write(f"**Score:** {round(article['similarity_score'], 2)}")

        st.subheader("Draft Response to User")
        st.text_area(
            "User-facing response",
            value=suggestion["user_response"],
            height=220
        )

        st.subheader("Internal Work Note")
        st.text_area(
            "Internal support note",
            value=suggestion["internal_work_note"],
            height=300
        )