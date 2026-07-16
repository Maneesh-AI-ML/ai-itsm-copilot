import sys
from pathlib import Path

import streamlit as st



# Allow this app file to import code from the src folder
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from triage_assistant import create_triage_suggestion
from agent_orchestrator import run_agent
from mock_writeback import save_mock_writeback

from audit_log import (
    save_agent_review_to_audit_log,
    save_review_to_audit_log,
)

st.set_page_config(
    page_title="AI ITSM Copilot",
    page_icon="🛠️",
    layout="wide",
)


# Create temporary memory for the latest triage suggestion
if "suggestion" not in st.session_state:
    st.session_state.suggestion = None

if "agent_result" not in st.session_state:
    st.session_state.agent_result = None

if "agent_review_status" not in st.session_state:
    st.session_state.agent_review_status = "Pending human review"

if "agent_response_editor" not in st.session_state:
    st.session_state.agent_response_editor = ""

if "agent_ticket_text" not in st.session_state:
    st.session_state.agent_ticket_text = ""

if "agent_writeback_result" not in st.session_state:
    st.session_state.agent_writeback_result = None

if "review_status" not in st.session_state:
    st.session_state.review_status = "Pending human review"

def save_current_review(review_status):
    suggestion = st.session_state.suggestion

    if suggestion is None:
        return

    save_review_to_audit_log(
        ticket_text=suggestion["new_ticket"],
        review_status=review_status,
        recommended_category=suggestion["recommended_category"],
        recommended_urgency=suggestion["recommended_urgency"],
        recommended_assignment_group=suggestion[
            "recommended_assignment_group"
        ],
        user_response=st.session_state.get(
            "user_response_editor",
            suggestion["user_response"],
        ),
        internal_work_note=st.session_state.get(
            "internal_work_note_editor",
            suggestion["internal_work_note"],
        ),
    )

    st.session_state.review_status = review_status


def approve_recommendation():
    save_current_review("Approved")

def save_current_agent_review(review_status):
    agent_result = st.session_state.agent_result

    if agent_result is None:
        return

    save_agent_review_to_audit_log(
        ticket_text=st.session_state.agent_ticket_text,
        review_status=review_status,
        agent_response=st.session_state.agent_response_editor,
        tool_trace=agent_result["tool_trace"],
    )

    st.session_state.agent_review_status = review_status


def approve_agent_result():
    save_current_agent_review("Approved")


def reject_recommendation():
    save_current_review("Rejected")


def reject_agent_result():
    save_current_agent_review("Rejected")

def mark_agent_as_edited():
    if st.session_state.agent_result is not None:
        st.session_state.agent_review_status = (
            "Edited - pending approval"
        )
        st.session_state.agent_writeback_result = None


def write_approved_agent_result():
    st.session_state.agent_writeback_result = save_mock_writeback(
        ticket_text=st.session_state.agent_ticket_text,
        review_status=st.session_state.agent_review_status,
        agent_response=st.session_state.agent_response_editor,
    )

def mark_as_edited():
    st.session_state.review_status = "Edited - pending approval"


st.title("AI ITSM Copilot")

st.write(
    "ServiceNow-style incident triage assistant for category, urgency, "
    "assignment group, similar tickets, knowledge articles, and support notes."
)


ticket_text = st.text_area(
    "Enter a new support ticket",
    placeholder="Example: VPN not working after password reset",
    height=120,
)


analyze_button = st.button("Analyze Ticket")
agent_button = st.button("Run Agentic Analysis")


if analyze_button:
    if not ticket_text.strip():
        st.warning("Please enter a ticket description.")
    else:
        st.session_state.suggestion = create_triage_suggestion(
            ticket_text
        )
        st.session_state.review_status = "Pending human review"
        
        st.session_state.pop("user_response_editor", None)
        st.session_state.pop("internal_work_note_editor", None)
if agent_button:
    if not ticket_text.strip():
        st.warning("Please enter a ticket description.")
    else:
        st.session_state.agent_review_status = "Pending human review"
        st.session_state.agent_writeback_result = None
        st.session_state.agent_ticket_text = ticket_text

        try:
            with st.spinner("Running agent tools..."):
                st.session_state.agent_result = run_agent(
                    ticket_text
                )

                st.session_state.agent_response_editor = (
                    st.session_state.agent_result["final_response"]
                )

        except Exception:
            st.session_state.agent_result = None
            st.session_state.agent_response_editor = ""

            st.error(
                "Agentic analysis is temporarily unavailable. "
                "You can still use Analyze Ticket for the reliable "
                "deterministic workflow."
            )

suggestion = st.session_state.suggestion
agent_result = st.session_state.agent_result

if agent_result is not None:
    st.subheader("Agentic Analysis")

    st.info(
        f"Agent review status: "
        f"{st.session_state.agent_review_status}"
    )

    st.text_area(
        "Editable Agent Response",
        key="agent_response_editor",
        height=220,
        on_change=mark_agent_as_edited,
    )

    st.button(
        "Approve Agent Result",
        on_click=approve_agent_result,
    )

    st.button(
        "Reject Agent Result",
        on_click=reject_agent_result,
    )

    st.button(
        "Write Approved Result Locally",
        on_click=write_approved_agent_result,
    )

    writeback_result = st.session_state.agent_writeback_result

    if writeback_result is not None:
        if writeback_result["success"]:
            st.success(writeback_result["message"])
        else:
            st.error(writeback_result["message"])

    st.subheader("Agent Tool Trace")

    for step in agent_result["tool_trace"]:
        with st.expander(step["tool_name"]):
            st.write("Arguments:")
            st.json(step["arguments"])

            st.write("Result:")
            st.json(step["result"])

if suggestion is not None:
    st.info(
        f"Review status: {st.session_state.review_status}"
    )

    st.subheader("Triage Recommendation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Category",
            suggestion["recommended_category"],
        )

    with col2:
        st.metric(
            "Urgency",
            suggestion["recommended_urgency"],
        )

    with col3:
        st.metric(
            "Assignment Group",
            suggestion["recommended_assignment_group"],
        )

    st.subheader("Similar Past Ticket")

    st.write(
        f"**Ticket ID:** "
        f"{suggestion['similar_ticket_id']}"
    )

    st.write(
        f"**Similarity Score:** "
        f"{round(suggestion['similarity_score'], 2)}"
    )

    st.write(
        f"**Confidence:** "
        f"{suggestion['confidence_status']}"
    )

    st.write(
        f"**Similar Ticket:** "
        f"{suggestion['similar_ticket_text']}"
    )

    st.subheader("Recommended Action")
    st.info(suggestion["recommended_action"])

    st.subheader("Suggested Resolution")
    st.write(suggestion["suggested_resolution"])

    st.subheader("Relevant Knowledge Articles")

    for article in suggestion["relevant_articles"]:
        with st.expander(
            f"{article['article_id']} - {article['title']}"
        ):
            st.write(
                f"**Category:** {article['category']}"
            )

            st.write(
                f"**Score:** "
                f"{round(article['similarity_score'], 2)}"
            )

            st.write(article["content"])
    st.caption(
    f"Response source: {suggestion['response_source']}"
)
    st.subheader("Draft Response to User")
    
    st.text_area(
    "User-facing response",
    value=suggestion["user_response"],
    height=220,
    key="user_response_editor",
    on_change=mark_as_edited,
)
    st.subheader("Internal Work Note")
    
    st.button(
        "Approve Recommendation",
        on_click=approve_recommendation,
    )

    st.button(
        "Reject Recommendation",
        on_click=reject_recommendation,
    )

    st.text_area(
        "Internal support note",
        value=suggestion["internal_work_note"],
        height=300,
        key="internal_work_note_editor",
        on_change=mark_as_edited,
    )