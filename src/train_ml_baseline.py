import json
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "public_support_tickets_processed.csv"
)
RESULTS_DIR = BASE_DIR / "docs" / "results"

RANDOM_STATE = 42
TEST_SIZE = 0.20


def load_dataset():
    """Load and validate the processed ITSM ticket dataset."""

    dataframe = pd.read_csv(DATA_PATH)

    required_columns = {"ticket_text", "category"}
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe = dataframe.dropna(
        subset=["ticket_text", "category"]
    ).copy()

    dataframe["ticket_text"] = (
        dataframe["ticket_text"].astype(str).str.strip()
    )
    dataframe["category"] = (
        dataframe["category"].astype(str).str.strip()
    )

    dataframe = dataframe[
        dataframe["ticket_text"].ne("")
        & dataframe["category"].ne("")
    ]

    return dataframe


def create_models():
    """Create two TF-IDF text-classification baselines."""

    tfidf_settings = {
        "lowercase": True,
        "ngram_range": (1, 2),
        "min_df": 2,
        "max_features": 20000,
        "sublinear_tf": True,
    }

    return {
        "Logistic Regression": Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(**tfidf_settings),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Linear SVM": Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(**tfidf_settings),
                ),
                (
                    "classifier",
                    LinearSVC(
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def evaluate_model(
    model_name,
    model,
    x_train,
    x_test,
    y_train,
    y_test,
):
    """Train one model and calculate evaluation metrics."""

    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "macro_f1": f1_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        ),
        "weighted_f1": f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        ),
    }

    report_text = classification_report(
        y_test,
        predictions,
        zero_division=0,
    )

    report_data = classification_report(
        y_test,
        predictions,
        zero_division=0,
        output_dict=True,
    )

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)
    print(f"Accuracy:    {metrics['accuracy']:.4f}")
    print(f"Macro F1:    {metrics['macro_f1']:.4f}")
    print(f"Weighted F1: {metrics['weighted_f1']:.4f}")
    print("\nClassification report:")
    print(report_text)

    return {
        "metrics": metrics,
        "classification_report": report_data,
        "report_text": report_text,
    }


def save_results(
    dataset_size,
    train_size,
    test_size,
    class_counts,
    results,
):
    """Save machine-readable and readable baseline reports."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = RESULTS_DIR / "ml_baseline_metrics.json"
    report_path = RESULTS_DIR / "ml_baseline_report.txt"

    json_payload = {
        "dataset_size": dataset_size,
        "train_size": train_size,
        "test_size": test_size,
        "random_state": RANDOM_STATE,
        "test_fraction": TEST_SIZE,
        "class_counts": class_counts,
        "models": {
            model_name: {
                "metrics": model_result["metrics"],
                "classification_report": model_result[
                    "classification_report"
                ],
            }
            for model_name, model_result in results.items()
        },
    }

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(json_payload, file, indent=2)

    report_lines = [
        "AI ITSM Copilot - ML Classification Baseline",
        "=" * 50,
        f"Dataset size: {dataset_size}",
        f"Training rows: {train_size}",
        f"Test rows: {test_size}",
        f"Random state: {RANDOM_STATE}",
        "",
        "Class counts:",
    ]

    for category, count in class_counts.items():
        report_lines.append(f"- {category}: {count}")

    for model_name, model_result in results.items():
        report_lines.extend(
            [
                "",
                "=" * 70,
                model_name,
                "=" * 70,
                (
                    "Accuracy: "
                    f"{model_result['metrics']['accuracy']:.4f}"
                ),
                (
                    "Macro F1: "
                    f"{model_result['metrics']['macro_f1']:.4f}"
                ),
                (
                    "Weighted F1: "
                    f"{model_result['metrics']['weighted_f1']:.4f}"
                ),
                "",
                model_result["report_text"],
            ]
        )

    report_path.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print("\nSaved results:")
    print(json_path)
    print(report_path)


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

    print(f"Dataset rows: {len(dataframe)}")
    print(f"Training rows: {len(x_train)}")
    print(f"Test rows: {len(x_test)}")

    class_counts = y.value_counts().sort_index().to_dict()

    print("\nClass counts:")
    for category, count in class_counts.items():
        print(f"- {category}: {count}")

    results = {}

    for model_name, model in create_models().items():
        results[model_name] = evaluate_model(
            model_name=model_name,
            model=model,
            x_train=x_train,
            x_test=x_test,
            y_train=y_train,
            y_test=y_test,
        )

    save_results(
        dataset_size=len(dataframe),
        train_size=len(x_train),
        test_size=len(x_test),
        class_counts=class_counts,
        results=results,
    )


if __name__ == "__main__":
    main()