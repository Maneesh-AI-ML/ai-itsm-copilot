from functools import lru_cache

from train_ml_baseline import (
    create_models,
    load_dataset,
)


@lru_cache(maxsize=1)
def get_ml_category_model():
    """
    Train and cache the final Linear SVM category model.

    The model is trained on the full processed dataset for
    application inference. Evaluation remains documented
    separately using the fixed held-out test split.
    """

    dataframe = load_dataset()

    model = create_models()["Linear SVM"]

    model.fit(
        dataframe["ticket_text"],
        dataframe["category"],
    )

    return model


def predict_ml_category(ticket_text):
    """
    Return ML category evidence for one support ticket.

    The decision margin is not a probability. It measures the
    distance between the strongest and second-strongest class scores.
    """

    cleaned_ticket = ticket_text.strip()

    if not cleaned_ticket:
        raise ValueError(
            "Ticket text cannot be empty."
        )

    model = get_ml_category_model()

    predicted_category = model.predict(
        [cleaned_ticket]
    )[0]

    decision_scores = model.decision_function(
        [cleaned_ticket]
    )[0]

    sorted_scores = sorted(
        decision_scores,
        reverse=True,
    )

    decision_margin = (
        sorted_scores[0] - sorted_scores[1]
    )

    return {
        "predicted_category": predicted_category,
        "decision_margin": float(decision_margin),
        "model_name": "Linear SVM",
        "evidence_type": "Supporting ML evidence",
        "is_probability": False,
    }