import json

from agent_tools import (
    classify_ticket_tool,
    search_knowledge_base_tool,
    search_similar_tickets_tool,
)
from llm_service import request_llm_tool_call


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "classify_ticket",
            "description": (
                "Classify an IT support ticket and recommend "
                "its category, urgency, and assignment group."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_text": {
                        "type": "string",
                        "description": (
                            "The complete support-ticket description."
                        ),
                    }
                },
                "required": ["ticket_text"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_similar_tickets",
            "description": (
                "Search historical IT support tickets and return "
                "similar resolved tickets."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_text": {
                        "type": "string",
                        "description": (
                            "The complete support-ticket description."
                        ),
                    },
                    "top_n": {
                        "type": "integer",
                        "description": (
                            "Number of similar tickets to return."
                        ),
                        "default": 1,
                    },
                },
                "required": ["ticket_text"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search IT support knowledge-base articles "
                "for relevant troubleshooting guidance."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_text": {
                        "type": "string",
                        "description": (
                            "The complete support-ticket description."
                        ),
                    },
                    "top_n": {
                        "type": "integer",
                        "description": (
                            "Number of knowledge articles to return."
                        ),
                        "default": 2,
                    },
                },
                "required": ["ticket_text"],
                "additionalProperties": False,
            },
        },
    },
]


TOOL_FUNCTIONS = {
    "classify_ticket": classify_ticket_tool,
    "search_similar_tickets": search_similar_tickets_tool,
    "search_knowledge_base": search_knowledge_base_tool,
}


REQUIRED_TOOLS = {
    "classify_ticket",
    "search_similar_tickets",
    "search_knowledge_base",
}

MAX_AGENT_ROUNDS = 6


def run_agent(ticket_text):
    """
    Run a controlled multi-tool ITSM agent workflow.

    The LLM chooses the tool order and tool arguments.
    The application limits execution to the approved tools.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are an ITSM triage agent. "
                "Before producing the final recommendation, collect "
                "ticket classification, similar-ticket evidence, and "
                "knowledge-base guidance using the available tools. "
                "Use each tool only once. "
                "Base the final answer only on the ticket and tool results. "
                "Never present details from a similar historical ticket as facts "
                "about the current user. Clearly label them as historical evidence. "
                "Do not invent facts, contact details, or completed actions."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Analyse this support ticket:\n{ticket_text}"
            ),
        },
    ]

    used_tools = set()
    tool_trace = []

    for _ in range(MAX_AGENT_ROUNDS):
        message = request_llm_tool_call(
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        # The model tried to answer before collecting all evidence.
        if not message.tool_calls:
            messages.append(
                message.model_dump(exclude_none=True)
            )

            missing_tools = REQUIRED_TOOLS - used_tools

            if missing_tools:
                missing_text = ", ".join(
                    sorted(missing_tools)
                )

                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Do not give the final answer yet. "
                            "Use one of these missing tools first: "
                            f"{missing_text}."
                        ),
                    }
                )

                continue

            return {
                "final_response": message.content or "",
                "tool_trace": tool_trace,
            }

        # Add the assistant's tool request to the conversation.
        messages.append(
            message.model_dump(exclude_none=True)
        )

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name

            try:
                tool_arguments = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError:
                tool_result = {
                    "error": "The tool arguments were not valid JSON."
                }

            else:
                tool_function = TOOL_FUNCTIONS.get(
                    tool_name
                )

                if tool_function is None:
                    tool_result = {
                        "error": (
                            f"Unknown tool requested: {tool_name}"
                        )
                    }

                elif tool_name in used_tools:
                    tool_result = {
                        "error": (
                            f"The tool {tool_name} was already used. "
                            "Choose a different missing tool."
                        )
                    }

                else:
                    tool_result = tool_function(
                        **tool_arguments
                    )

                    used_tools.add(tool_name)

                    tool_trace.append(
                        {
                            "tool_name": tool_name,
                            "arguments": tool_arguments,
                            "result": tool_result,
                        }
                    )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

        # Once all three tools have run, prevent further tool calls
        # and request the final grounded recommendation.
        if REQUIRED_TOOLS.issubset(used_tools):
            final_message = request_llm_tool_call(
                messages=messages,
                tools=TOOLS,
                tool_choice="none",
            )

            return {
                "final_response": final_message.content or "",
                "tool_trace": tool_trace,
            }

    # Safety fallback if the model keeps repeating or refusing tools.
    final_message = request_llm_tool_call(
        messages=messages,
        tools=TOOLS,
        tool_choice="none",
    )

    return {
        "final_response": final_message.content or "",
        "tool_trace": tool_trace,
    }


if __name__ == "__main__":
    result = run_agent(
        "VPN is not connecting after I changed my password."
    )

    print("\nExecuted tools:")

    for step in result["tool_trace"]:
        print(f"- {step['tool_name']}")

    print("\nFinal agent response:")
    print(result["final_response"])