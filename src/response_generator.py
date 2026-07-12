def generate_user_response(ticket_text, category, assignment_group, suggested_resolution, confidence_status):
    """
    Generate a simple support response draft for the end user.
    This is visible to the requester.
    """

    if confidence_status == "High enough":
        response = (
            f"Hello,\n\n"
            f"Thank you for reporting the issue.\n\n"
            f"Based on your description, this appears to be related to {category}.\n"
            f"Suggested first step: {suggested_resolution}.\n\n"
            f"If the issue continues, the ticket should be handled by {assignment_group}.\n\n"
            f"Best regards,\n"
            f"IT Support"
        )
    else:
        response = (
            f"Hello,\n\n"
            f"Thank you for reporting the issue.\n\n"
            f"We could not find a reliable matching past resolution for this request.\n"
            f"The ticket should be reviewed by a human support agent.\n\n"
            f"Best regards,\n"
            f"IT Support"
        )

    return response


def generate_internal_work_note(
    category,
    urgency,
    assignment_group,
    similar_ticket_id,
    similarity_score,
    suggested_resolution,
    relevant_articles,
    confidence_status,
    recommended_action
):
    """
    Generate an internal work note for the support team.
    This is not meant for the end user.
    """

    article_lines = []

    for article in relevant_articles:
        article_lines.append(
            f"- {article['article_id']}: {article['title']} "
            f"(score: {round(article['similarity_score'], 2)})"
        )

    articles_text = "\n".join(article_lines)

    work_note = (
        f"AI ITSM Copilot internal triage note:\n\n"
        f"Recommended category: {category}\n"
        f"Recommended urgency: {urgency}\n"
        f"Recommended assignment group: {assignment_group}\n"
        f"Confidence status: {confidence_status}\n"
        f"Recommended action: {recommended_action}\n\n"
        f"Most similar past ticket: {similar_ticket_id}\n"
        f"Similarity score: {round(similarity_score, 2)}\n\n"
        f"Suggested resolution:\n"
        f"{suggested_resolution}\n\n"
        f"Relevant knowledge articles:\n"
        f"{articles_text}"
    )

    return work_note