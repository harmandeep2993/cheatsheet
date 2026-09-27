"""Tests for the tool agent: safe calculator, error handling and the loop, all without an API key."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from conftest import fake_text_message, fake_tool_use_message
from tool_agent.agent import run_agent, run_tool
from tool_agent.tools import calculate, get_order_status


@pytest.mark.parametrize(
    ("expression", "expected"),
    [("2 + 3 * 4", "14"), ("(10 - 4) / 3", "2.0"), ("-2 ** 2", "-4")],
)
def test_calculate(expression, expected):
    assert calculate(expression) == expected


@pytest.mark.parametrize("expression", ["__import__('os').system('dir')", "open('x')", "2 ** 1000000"])
def test_calculate_rejects_unsafe_input(expression):
    with pytest.raises(ValueError):
        calculate(expression)


def test_get_order_status_normalises_id():
    assert "shipped" in get_order_status(" a-1042 ")


def test_run_tool_reports_errors_to_the_model():
    unknown = run_tool(SimpleNamespace(name="delete_everything", input={}, id="t1"))
    missing = run_tool(SimpleNamespace(name="get_order_status", input={"order_id": "Z-9"}, id="t2"))
    assert unknown["is_error"] and "Unknown tool" in unknown["content"]
    assert missing["is_error"] and "Not found" in missing["content"]


def test_agent_calls_tool_then_answers():
    client = MagicMock()
    client.messages.create.side_effect = [
        fake_tool_use_message("get_order_status", {"order_id": "A-1042"}),
        fake_text_message("Your order shipped and arrives on 2026-09-30."),
    ]

    result = run_agent(client, "Where is A-1042?")

    assert result.steps == 2
    assert result.tool_calls[0]["name"] == "get_order_status"
    assert "2026-09-30" in result.answer
    # The agent keeps appending to the same list, so find the tool results by role, not position
    messages = client.messages.create.call_args_list[1].kwargs["messages"]
    results_msg = next(m for m in messages if m["role"] == "user" and isinstance(m["content"], list))
    tool_result = results_msg["content"][0]
    assert tool_result["type"] == "tool_result" and tool_result["tool_use_id"] == "toolu_1"


def test_agent_stops_at_step_limit():
    client = MagicMock()
    client.messages.create.return_value = fake_tool_use_message("calculate", {"expression": "1 + 1"})

    result = run_agent(client, "loop forever", max_steps=3)

    assert result.answer.startswith("Stopped")
    assert client.messages.create.call_count == 3
