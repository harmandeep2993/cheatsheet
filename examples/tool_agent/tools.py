"""Tools the agent can call: a safe calculator and an order lookup, plus their JSON schemas."""

import ast
import operator
from collections.abc import Callable

# Demo data; a real app would query a database or API here
ORDERS = {
    "A-1042": {"status": "shipped", "eta": "2026-09-30"},
    "A-2001": {"status": "processing", "eta": None},
}

# Only plain arithmetic is allowed, so model-provided input can never run arbitrary code
_OPERATORS: dict[type, Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}
MAX_EXPONENT = 100


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        # Guard against huge powers that would hang the process
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError("exponent too large")
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("only numbers and + - * / // % ** are allowed")


def calculate(expression: str) -> str:
    """Evaluate an arithmetic expression safely and return the result as text."""
    tree = ast.parse(expression, mode="eval")
    return str(_evaluate(tree.body))


def get_order_status(order_id: str) -> str:
    """Return the status and ETA of an order, or raise KeyError if it does not exist."""
    order = ORDERS[order_id.strip().upper()]
    return f"status={order['status']}, eta={order['eta'] or 'unknown'}"


TOOLS = [
    {
        "name": "calculate",
        "description": (
            "Evaluate an arithmetic expression exactly, e.g. '12.5 * 3 + 7'. Use this for any maths "
            "instead of calculating in your head. Supports + - * / // % ** and parentheses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "Arithmetic expression"}},
            "required": ["expression"],
        },
    },
    {
        "name": "get_order_status",
        "description": (
            "Look up the shipping status and estimated delivery date of an order. Use it whenever the "
            "user asks where an order is. Returns status and eta."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "Order number, format A-1234"}},
            "required": ["order_id"],
        },
    },
]

HANDLERS: dict[str, Callable[..., str]] = {
    "calculate": calculate,
    "get_order_status": get_order_status,
}
