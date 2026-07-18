import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


import ml_classifier


class FakePredictionModel:
    def predict(self, ticket_texts):
        return ["Access"]

    def decision_function(self, ticket_texts):
        return [[0.10, 1.20, 0.50]]


class FakeTrainingModel:
    def __init__(self):
        self.fit_calls = []

    def fit(self, ticket_texts, categories):
        self.fit_calls.append(
            (ticket_texts, categories)
        )
        return self


class TestMLClassifier(unittest.TestCase):
    def tearDown(self):
        ml_classifier.get_ml_category_model.cache_clear()

    def test_predict_ml_category_returns_supporting_evidence(self):
        with patch(
            "ml_classifier.get_ml_category_model",
            return_value=FakePredictionModel(),
        ):
            result = ml_classifier.predict_ml_category(
                "VPN is not working after password reset"
            )

        self.assertEqual(
            result["predicted_category"],
            "Access",
        )
        self.assertAlmostEqual(
            result["decision_margin"],
            0.70,
        )
        self.assertEqual(
            result["model_name"],
            "Linear SVM",
        )
        self.assertEqual(
            result["evidence_type"],
            "Supporting ML evidence",
        )
        self.assertFalse(result["is_probability"])

    def test_predict_ml_category_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            ml_classifier.predict_ml_category("   ")

    def test_model_is_trained_once_and_cached(self):
        fake_dataframe = {
            "ticket_text": ["VPN issue", "Email issue"],
            "category": ["Network", "Email"],
        }
        fake_model = FakeTrainingModel()

        ml_classifier.get_ml_category_model.cache_clear()

        with patch(
            "ml_classifier.load_dataset",
            return_value=fake_dataframe,
        ), patch(
            "ml_classifier.create_models",
            return_value={"Linear SVM": fake_model},
        ):
            first_model = (
                ml_classifier.get_ml_category_model()
            )
            second_model = (
                ml_classifier.get_ml_category_model()
            )

        self.assertIs(first_model, fake_model)
        self.assertIs(second_model, fake_model)
        self.assertEqual(len(fake_model.fit_calls), 1)
        self.assertEqual(
            fake_model.fit_calls[0][0],
            fake_dataframe["ticket_text"],
        )
        self.assertEqual(
            fake_model.fit_calls[0][1],
            fake_dataframe["category"],
        )


if __name__ == "__main__":
    unittest.main()