
import ast
import operator
import re
import sqlite3
from pathlib import Path


# ---------- Calculator tool ----------

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def calculate(expression: str) -> str:
    """Calculate basic arithmetic using +, -, *, and /."""

    def evaluate(node):
        if (
            isinstance(node, ast.Constant)
            and type(node.value) in (int, float)
        ):
            return node.value

        if (
            isinstance(node, ast.BinOp)
            and type(node.op) in _OPERATORS
        ):
            left = evaluate(node.left)
            right = evaluate(node.right)
            return _OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)
        ):
            value = evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value

        raise ValueError("Only basic arithmetic is allowed.")

    try:
        result = evaluate(ast.parse(expression, mode="eval").body)
        return str(result)
    except (
        ValueError,
        TypeError,
        ZeroDivisionError,
        SyntaxError,
    ) as error:
        return f"Calculation error: {error}"


# ---------- Database configuration ----------

DB_PATH = Path(__file__).with_name("business.db")


# ---------- Order lookup tool ----------

def lookup_order(order_id: str) -> dict:
    """Look up a business order from the SQLite database."""

    order_id = order_id.strip().upper()

    if not re.fullmatch(r"ORD-\d{4}", order_id):
        return {"error": "Invalid order ID format."}

    try:
        with sqlite3.connect(DB_PATH) as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                SELECT order_id, status, customer,
                       product, quantity, total_gbp
                FROM orders
                WHERE order_id = ?
                """,
                (order_id,),
            ).fetchone()

    except sqlite3.Error:
        return {"error": "Database lookup failed."}

    if row is None:
        return {"error": "Order not found."}

    return {
        "order_id": row["order_id"],
        "status": row["status"],
        "customer": row["customer"],
        "items": [
            {
                "product": row["product"],
                "quantity": row["quantity"],
            }
        ],
        "total_gbp": row["total_gbp"],
    }
