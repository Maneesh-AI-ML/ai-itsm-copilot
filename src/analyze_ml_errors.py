from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from train_ml_baseline import (
    RANDOM_STATE,
    TEST_SIZE,
    create_models,
    load_dataset,
)


BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "docs" / "results"


def save_confusion_matrix_image(
    matrix,
    labels,
):
    """
    Save a readable confusion-matrix image.
    """

    image_path = (
        RESULTS_DIR
        / "ml_confusion_matrix.png"
    )

    plt.figure(figsize=(10, 8))

    image = plt.imshow(matrix)
    plt.colorbar(image)

    positions = range(len(labels))

    plt.xticks(
        positions,
        labels,
        rotation=45,
        ha="right",
    )

    plt.yticks(
        positions,
        labels,
    )

    plt.xlabel("Predicted category")
    plt.ylabel("Actual category")
    plt.title(
        "Linear SVM Ticket Classification Confusion Matrix"
    )

    for row_index in positions:
        for column_index in positions:
            value = matrix[
                row_index,
                column_index,
            ]

            plt.text(
                column_index,
                row_index,
                str(value),
                ha="center",
                va="center",
            )

    plt.tight_layout()

    plt.savefig(
        image_path,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()

    return image_path


def main():
    dataframe = load_dataset()

    x = dataframe["ticket_text"]
    y = dataframe["category"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = create_models()["Linear SVM"]
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    labels = sorted(y.unique())

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    matrix_dataframe = pd.DataFrame(
        matrix,
        index=[
            f"Actual: {label}"
            for label in labels
        ],
        columns=[
            f"Predicted: {label}"
            for label in labels
        ],
    )

    error_dataframe = pd.DataFrame(
        {
            "ticket_text": x_test.values,
            "actual_category": y_test.values,
            "predicted_category": predictions,
        }
    )

    error_dataframe = error_dataframe[
        error_dataframe["actual_category"]
        != error_dataframe["predicted_category"]
    ].copy()

    top_confusions = (
        error_dataframe
        .groupby(
            [
                "actual_category",
                "predicted_category",
            ]
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            by="count",
            ascending=False,
        )
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    matrix_path = (
        RESULTS_DIR
        / "ml_confusion_matrix.csv"
    )

    confusion_path = (
        RESULTS_DIR
        / "ml_top_confusions.csv"
    )

    examples_path = (
        RESULTS_DIR
        / "ml_misclassified_examples.csv"
    )

    matrix_dataframe.to_csv(
        matrix_path,
        encoding="utf-8",
    )

    top_confusions.to_csv(
        confusion_path,
        index=False,
        encoding="utf-8",
    )

    error_dataframe.to_csv(
        examples_path,
        index=False,
        encoding="utf-8",
    )

    image_path = save_confusion_matrix_image(
        matrix=matrix,
        labels=labels,
    )

    total_test_rows = len(y_test)
    total_errors = len(error_dataframe)

    print(
        f"Test rows: {total_test_rows}"
    )
    print(
        f"Misclassified rows: {total_errors}"
    )
    print(
        "Correct rows: "
        f"{total_test_rows - total_errors}"
    )

    print("\nTop category confusions:")

    if top_confusions.empty:
        print("No misclassifications found.")
    else:
        print(
            top_confusions
            .head(10)
            .to_string(index=False)
        )

    print("\nSaved files:")
    print(matrix_path)
    print(confusion_path)
    print(examples_path)
    print(image_path)


if __name__ == "__main__":
    main()