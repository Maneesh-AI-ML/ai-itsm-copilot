import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


import agent_orchestrator
import agent_tools
import audit_log
import mock_writeback
import triage_assistant


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(self, content="", tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []

    def model_dump(self, exclude_none=True):
        return {
            "role": "assistant",
            "content": self.content,
        }


class TestAgentTools(unittest.TestCase):
    def test_classify_ticket_tool(self):
        with patch(
            "agent_tools.classify_ticket",
            return_value=("Network", "Medium", "Network Support"),
        ):
            result = agent_tools.classify_ticket_tool(
                "VPN is not working."
            )

        self.assertEqual(result["category"], "Network")
        self.assertEqual(result["urgency"], "Medium")
        self.assertEqual(
            result["assignment_group"],
            "Network Support",
        )

    def test_search_similar_tickets_tool(self):
        fake_match = {
            "ticket_id": "INC001",
            "ticket_text": "VPN connection problem",
            "category": "Network",
            "urgency": "Medium",
            "assignment_group": "Network Support",
            "resolution": "Reset the VPN profile.",
            "similarity_score": 0.82,
        }

        with patch(
            "agent_tools.load_tickets",
            return_value=["fake-ticket-data"],
        ), patch(
            "agent_tools.find_similar_tickets",
            return_value=[fake_match],
        ):
            result = agent_tools.search_similar_tickets_tool(
                "VPN is not working.",
                top_n=1,
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ticket_id"], "INC001")
        self.assertIsInstance(
            result[0]["similarity_score"],
            float,
        )

    def test_search_knowledge_base_tool(self):
        fake_article = {
            "article_id": "KB001",
            "title": "VPN Troubleshooting Guide",
            "category": "Network",
            "content": "Check the VPN profile and password.",
            "similarity_score": 0.75,
        }

        with patch(
            "agent_tools.find_relevant_articles",
            return_value=[fake_article],
        ):
            result = agent_tools.search_knowledge_base_tool(
                "VPN is not working.",
                top_n=1,
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["article_id"], "KB001")
        self.assertIsInstance(
            result[0]["similarity_score"],
            float,
        )


class TestAgentOrchestrator(unittest.TestCase):
    def test_agent_runs_required_tools_and_keeps_trace(self):
        responses = [
            FakeMessage(
                tool_calls=[
                    FakeToolCall(
                        "call-1",
                        "classify_ticket",
                        '{"ticket_text": "VPN not working"}',
                    )
                ]
            ),
            FakeMessage(
                tool_calls=[
                    FakeToolCall(
                        "call-2",
                        "search_similar_tickets",
                        (
                            '{"ticket_text": "VPN not working", '
                            '"top_n": 1}'
                        ),
                    )
                ]
            ),
            FakeMessage(
                tool_calls=[
                    FakeToolCall(
                        "call-3",
                        "search_knowledge_base",
                        (
                            '{"ticket_text": "VPN not working", '
                            '"top_n": 2}'
                        ),
                    )
                ]
            ),
            FakeMessage(
                content="Final grounded agent recommendation."
            ),
        ]

        fake_tools = {
            "classify_ticket": lambda ticket_text: {
                "category": "Network",
                "urgency": "Medium",
                "assignment_group": "Network Support",
            },
            "search_similar_tickets": (
                lambda ticket_text, top_n=1: [
                    {
                        "ticket_id": "INC001",
                        "historical_evidence": True,
                    }
                ]
            ),
            "search_knowledge_base": (
                lambda ticket_text, top_n=2: [
                    {
                        "article_id": "KB001",
                        "content": "Reset the VPN profile.",
                    }
                ]
            ),
        }

        with patch(
            "agent_orchestrator.request_llm_tool_call",
            side_effect=responses,
        ), patch.dict(
            agent_orchestrator.TOOL_FUNCTIONS,
            fake_tools,
            clear=True,
        ):
            result = agent_orchestrator.run_agent(
                "VPN not working"
            )

        self.assertEqual(
            result["final_response"],
            "Final grounded agent recommendation.",
        )

        tool_names = [
            step["tool_name"]
            for step in result["tool_trace"]
        ]

        self.assertEqual(
            tool_names,
            [
                "classify_ticket",
                "search_similar_tickets",
                "search_knowledge_base",
            ],
        )

        self.assertEqual(len(result["tool_trace"]), 3)


class TestAgentAuditLog(unittest.TestCase):
    def test_approved_and_rejected_decisions_are_saved(self):
        tool_trace = [
            {
                "tool_name": "classify_ticket",
                "arguments": {
                    "ticket_text": "VPN not working"
                },
                "result": {
                    "category": "Network"
                },
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_path = (
                Path(temp_dir) / "agent_audit_log.csv"
            )

            with patch.object(
                audit_log,
                "AGENT_AUDIT_LOG_PATH",
                audit_path,
            ):
                audit_log.save_agent_review_to_audit_log(
                    ticket_text="VPN not working",
                    review_status="Approved",
                    agent_response="Approved response",
                    tool_trace=tool_trace,
                )

                audit_log.save_agent_review_to_audit_log(
                    ticket_text="VPN not working",
                    review_status="Rejected",
                    agent_response="Rejected response",
                    tool_trace=tool_trace,
                )

            with open(
                audit_path,
                encoding="utf-8",
                newline="",
            ) as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 2)
        self.assertEqual(
            rows[0]["review_status"],
            "Approved",
        )
        self.assertEqual(
            rows[1]["review_status"],
            "Rejected",
        )
        self.assertEqual(
            rows[0]["tools_used"],
            "classify_ticket",
        )


class TestMockWriteback(unittest.TestCase):
    def test_writeback_is_blocked_without_approval(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            writeback_path = (
                Path(temp_dir) / "mock_writeback.csv"
            )

            with patch.object(
                mock_writeback,
                "MOCK_WRITEBACK_PATH",
                writeback_path,
            ):
                result = mock_writeback.save_mock_writeback(
                    ticket_text="VPN not working",
                    review_status="Rejected",
                    agent_response="Do not write this.",
                )

            self.assertFalse(result["success"])
            self.assertFalse(writeback_path.exists())

    def test_approved_result_is_written(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            writeback_path = (
                Path(temp_dir) / "mock_writeback.csv"
            )

            with patch.object(
                mock_writeback,
                "MOCK_WRITEBACK_PATH",
                writeback_path,
            ):
                result = mock_writeback.save_mock_writeback(
                    ticket_text="VPN not working",
                    review_status="Approved",
                    agent_response="Approved recommendation.",
                )

            self.assertTrue(result["success"])
            self.assertTrue(writeback_path.exists())

            with open(
                writeback_path,
                encoding="utf-8",
                newline="",
            ) as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["review_status"],
            "Approved",
        )


class TestTemplateFallback(unittest.TestCase):
    def test_template_response_is_used_when_llm_fails(self):
        fake_ticket = {
            "ticket_id": "INC001",
            "ticket_text": "Historical VPN problem",
            "category": "Network",
            "urgency": "Medium",
            "assignment_group": "Network Support",
            "resolution": "Please contact us at",
            "similarity_score": 0.80,
        }

        fake_article = {
            "article_id": "KB001",
            "title": "VPN Troubleshooting Guide",
            "category": "Network",
            "content": "Reset the VPN profile.",
            "similarity_score": 0.75,
        }

        with patch(
            "triage_assistant.load_tickets",
            return_value=["fake-ticket-data"],
        ), patch(
            "triage_assistant.classify_ticket",
            return_value=(
                "Network",
                "Medium",
                "Network Support",
            ),
        ), patch(
            "triage_assistant.find_similar_tickets",
            return_value=[fake_ticket],
        ), patch(
            "triage_assistant.find_relevant_articles",
            return_value=[fake_article],
        ), patch(
            "triage_assistant.generate_llm_user_response",
            side_effect=RuntimeError("LLM unavailable"),
        ), patch(
            "triage_assistant.generate_user_response",
            return_value="Template fallback response",
        ), patch(
            "triage_assistant.generate_internal_work_note",
            return_value="Internal work note",
        ):
            result = (
                triage_assistant.create_triage_suggestion(
                    "VPN not working"
                )
            )

        self.assertEqual(
            result["response_source"],
            "Template fallback",
        )
        self.assertEqual(
            result["user_response"],
            "Template fallback response",
        )
        self.assertEqual(
            result["suggested_resolution"],
            "Reset the VPN profile.",
        )


if __name__ == "__main__":
    unittest.main()