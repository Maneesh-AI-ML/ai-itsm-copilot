from llm_service import generate_llm_text


def generate_llm_user_response(
    ticket_text,
    category,
    urgency,
    assignment_group,
    suggested_resolution,
    relevant_articles,
    confidence_status,
):
    """
    Generate a professional customer-facing response using an LLM.
    """

    knowledge_context = "\n\n".join(
    (
        f"{article['article_id']} - {article['title']}:\n"
        f"{article['content']}"
    )
    for article in relevant_articles
)

    if confidence_status == "Low confidence":
        review_instruction = (
            "Tell the user that a human support agent will review the ticket."
        )
    else:
        review_instruction = (
            "Do not mention human review, low confidence, or uncertainty."
        )

    prompt = f"""
Write a short and professional IT support response to the user.

Original ticket:
{ticket_text}

Recommended category:
{category}

Recommended urgency:
{urgency}

Recommended assignment group:
{assignment_group}

Suggested resolution:
{suggested_resolution}

Relevant knowledge articles:
{knowledge_context}

Confidence status:
{confidence_status}

Requirements:
- Do not invent facts.
- Do not claim that the issue is already resolved.
- Explain the recommended next step clearly.
- {review_instruction}
- Keep the response under 180 words.
- End with "Best regards, IT Support".
- Do not invent phone numbers, email addresses, names, links, or contact details.
- Do not include a subject line.
"""

    return generate_llm_text(prompt)


if __name__ == "__main__":
    test_articles = [
        {
            "title": "VPN Troubleshooting Guide",
        }
    ]

    response = generate_llm_user_response(
        ticket_text=(
            "VPN is not connecting after I changed my password."
        ),
        category="Network",
        urgency="Medium",
        assignment_group="Network Support",
        suggested_resolution=(
            "Reset the VPN profile and verify MFA access."
        ),
        relevant_articles=test_articles,
        confidence_status="High enough",
    )

    print(response)