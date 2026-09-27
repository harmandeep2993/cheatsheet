"""Shared test helpers: fake Claude responses so every example is testable without an API key."""

from types import SimpleNamespace


def fake_text_message(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    """A stand-in for an Anthropic Message containing one text block."""
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=10, output_tokens=5),
    )


def fake_tool_use_message(name: str, tool_input: dict, tool_id: str = "toolu_1") -> SimpleNamespace:
    """A stand-in for a Message in which the model asks to call one tool."""
    return SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name=name, input=tool_input, id=tool_id)],
        stop_reason="tool_use",
        usage=SimpleNamespace(input_tokens=10, output_tokens=5),
    )
