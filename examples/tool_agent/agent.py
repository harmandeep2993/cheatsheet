"""A minimal agent loop: the model calls tools until it can answer, with a hard step limit.

Run:  uv run python -m tool_agent.agent "Where is order A-1042 and what is 17% of 249?"
Guide: 28_tool-use.md, 31_ai-agents.md
"""

import logging
import os
import sys
from dataclasses import dataclass, field

import anthropic

from tool_agent.tools import HANDLERS, TOOLS

logger = logging.getLogger(__name__)

MODEL = os.getenv("LLM_MODEL", "claude-opus-5")
MAX_TOKENS = 16000
# Hard cap so a confused model can never loop (and spend) forever
MAX_STEPS = 8
SYSTEM = (
    "You are a helpful support assistant. Use the tools for order lookups and for any arithmetic. "
    "When you have the answer, reply briefly and mention which facts came from tools."
)


@dataclass
class AgentResult:
    """Final answer plus a trace of what the agent did."""

    answer: str
    steps: int
    tool_calls: list[dict] = field(default_factory=list)


def run_tool(block) -> dict:
    """Execute one tool_use block and return the matching tool_result block."""
    handler = HANDLERS.get(block.name)
    if handler is None:
        return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                "content": f"Unknown tool '{block.name}'."}
    try:
        output = handler(**block.input)
    except KeyError:
        return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                "content": "Not found. Ask the user to check the order number (format A-1234)."}
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as exc:
        return {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                "content": f"Invalid input: {exc}"}
    return {"type": "tool_result", "tool_use_id": block.id, "content": output}


def run_agent(client, goal: str, max_steps: int = MAX_STEPS) -> AgentResult:
    """Run the tool loop until the model stops asking for tools or the step limit is hit.

    Args:
        client: an anthropic.Anthropic client (or a test double).
        goal: the user's request.
        max_steps: maximum number of model calls.

    Returns:
        AgentResult with the final text, number of steps and every tool call made.
    """
    messages = [{"role": "user", "content": goal}]
    tool_calls: list[dict] = []
    for step in range(1, max_steps + 1):
        response = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM, tools=TOOLS, messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            answer = "".join(b.text for b in response.content if b.type == "text")
            return AgentResult(answer=answer, steps=step, tool_calls=tool_calls)

        results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block)
                tool_calls.append({"name": block.name, "input": block.input, "result": result["content"]})
                results.append(result)
        # All results go back in ONE user message, which keeps parallel tool calls working
        messages.append({"role": "user", "content": results})

    return AgentResult(answer="Stopped: step limit reached.", steps=max_steps, tool_calls=tool_calls)


def main() -> None:
    """Run the agent on a goal from the command line."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    goal = " ".join(sys.argv[1:]) or "Where is order A-1042, and what is 17% of 249?"
    result = run_agent(anthropic.Anthropic(), goal)
    for call in result.tool_calls:
        logger.info("tool %s(%s) -> %s", call["name"], call["input"], call["result"])
    logger.info("answer (%d steps): %s", result.steps, result.answer)


if __name__ == "__main__":
    main()
