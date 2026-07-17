import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


import servicenow_service


class TestServiceNowService(unittest.TestCase):
    def setUp(self):
        self.instance_patch = patch.object(
            servicenow_service,
            "SERVICENOW_INSTANCE_URL",
            "https://example.service-now.com",
        )
        self.username_patch = patch.object(
            servicenow_service,
            "SERVICENOW_USERNAME",
            "test-user",
        )
        self.password_patch = patch.object(
            servicenow_service,
            "SERVICENOW_PASSWORD",
            "test-password",
        )

        self.instance_patch.start()
        self.username_patch.start()
        self.password_patch.start()

        self.addCleanup(self.instance_patch.stop)
        self.addCleanup(self.username_patch.stop)
        self.addCleanup(self.password_patch.stop)

    def test_get_incident_by_number_returns_incident(self):
        fake_response = Mock()
        fake_response.json.return_value = {
            "result": [
                {
                    "sys_id": "abc123",
                    "number": "INC0010010",
                    "short_description": "VPN not working",
                }
            ]
        }

        with patch(
            "servicenow_service.requests.get",
            return_value=fake_response,
        ) as mock_get:
            result = servicenow_service.get_incident_by_number(
                "INC0010010"
            )

        self.assertEqual(result["sys_id"], "abc123")
        self.assertEqual(result["number"], "INC0010010")

        fake_response.raise_for_status.assert_called_once_with()
        mock_get.assert_called_once()

        request_kwargs = mock_get.call_args.kwargs

        self.assertEqual(
            request_kwargs["params"]["sysparm_query"],
            "number=INC0010010",
        )
        self.assertEqual(
            request_kwargs["auth"],
            ("test-user", "test-password"),
        )
        self.assertEqual(request_kwargs["timeout"], 20)

    def test_get_incident_by_number_returns_none_when_missing(self):
        fake_response = Mock()
        fake_response.json.return_value = {
            "result": []
        }

        with patch(
            "servicenow_service.requests.get",
            return_value=fake_response,
        ):
            result = servicenow_service.get_incident_by_number(
                "INC9999999"
            )

        self.assertIsNone(result)
        fake_response.raise_for_status.assert_called_once_with()

    def test_add_work_note_sends_patch_request(self):
        fake_response = Mock()
        fake_response.json.return_value = {
            "result": {
                "sys_id": "abc123",
                "number": "INC0010010",
            }
        }

        with patch(
            "servicenow_service.requests.patch",
            return_value=fake_response,
        ) as mock_patch:
            result = (
                servicenow_service.add_work_note_to_incident(
                    incident_sys_id="abc123",
                    work_note="Approved recommendation.",
                )
            )

        self.assertEqual(result["sys_id"], "abc123")

        fake_response.raise_for_status.assert_called_once_with()
        mock_patch.assert_called_once()

        request_url = mock_patch.call_args.args[0]
        request_kwargs = mock_patch.call_args.kwargs

        self.assertEqual(
            request_url,
            (
                "https://example.service-now.com"
                "/api/now/v1/table/incident/abc123"
            ),
        )
        self.assertEqual(
            request_kwargs["json"],
            {
                "work_notes": "Approved recommendation.",
            },
        )
        self.assertEqual(
            request_kwargs["auth"],
            ("test-user", "test-password"),
        )
        self.assertEqual(request_kwargs["timeout"], 20)

    def test_add_work_note_rejects_missing_sys_id(self):
        with patch(
            "servicenow_service.requests.patch"
        ) as mock_patch:
            with self.assertRaises(ValueError):
                servicenow_service.add_work_note_to_incident(
                    incident_sys_id="",
                    work_note="Approved recommendation.",
                )

        mock_patch.assert_not_called()

    def test_add_work_note_rejects_empty_note(self):
        with patch(
            "servicenow_service.requests.patch"
        ) as mock_patch:
            with self.assertRaises(ValueError):
                servicenow_service.add_work_note_to_incident(
                    incident_sys_id="abc123",
                    work_note="   ",
                )

        mock_patch.assert_not_called()

    def test_missing_configuration_blocks_request(self):
        with patch.object(
            servicenow_service,
            "SERVICENOW_PASSWORD",
            "",
        ), patch(
            "servicenow_service.requests.get"
        ) as mock_get:
            with self.assertRaises(RuntimeError):
                servicenow_service.get_incident_by_number(
                    "INC0010010"
                )

        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()