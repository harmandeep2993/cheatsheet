"""Tests for llm_basics using a fake client (no API key or network needed)."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from conftest import fake_text_message
from llm_basics.basics import Ticket, ask, classify_ticket, text_of


def test_ask_returns_text_and_sends_question():
    client = MagicMock()
    client.messages.create.return_value = fake_text_message("RAG retrieves documents first.")

    answer = ask(client, "What is RAG?")

    assert answer == "RAG retrieves documents first."
    sent = client.messages.create.call_args.kwargs
    assert sent["messages"] == [{"role": "user", "content": "What is RAG?"}]
    assert "concise" in sent["system"]


def test_text_of_skips_non_text_blocks():
    response = SimpleNamespace(content=[
        SimpleNamespace(type="thinking", thinking="..."),
        SimpleNamespace(type="text", text="Hello "),
        SimpleNamespace(type="text", text="world"),
    ])
    assert text_of(response) == "Hello world"


def test_ask_warns_when_cut_off(caplog):
    client = MagicMock()
    client.messages.create.return_value = fake_text_message("partial", stop_reason="max_tokens")
    with caplog.at_level("WARNING"):
        ask(client, "long question")
    assert "max_tokens" in caplog.text


def test_classify_ticket_returns_parsed_output():
    ticket = Ticket(category="billing", urgency=4, summary="Charged twice")
    client = MagicMock()
    client.messages.parse.return_value = SimpleNamespace(parsed_output=ticket)

    assert classify_ticket(client, "charged twice") == ticket
    assert client.messages.parse.call_args.kwargs["output_format"] is Ticket


def test_ticket_rejects_invalid_urgency():
    with pytest.raises(ValidationError):
        Ticket(category="billing", urgency=9, summary="x")
