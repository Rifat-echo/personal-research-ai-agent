
import logging
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import calculate, lookup_order
from market_tools import get_market_trend


# ---------- Configuration ----------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.5-flash-lite"
MAX_TOOL_ROUNDS = 3


# ---------- Logging ----------

logger = logging.getLogger("business_agent")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s"
    )

    file_handler = logging.FileHandler(
        "agent.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# ---------- Approved tools ----------

TOOL_REGISTRY = {
    "calculate": calculate,
    "lookup_order": lookup_order,
    "get_market_trend": get_market_trend,
}


# ---------- Agent runtime ----------

def run_agent(question: str, history: list) -> str:
    """Run a request while preserving conversation history."""

    history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=question)],
        )
    )

    tool_rounds = 0

    while True:
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(
                tools=list(TOOL_REGISTRY.values()),
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),
            ),
        )

        function_calls = response.function_calls or []

        # No tool calls means Gemini has finished answering.
        if not function_calls:
            if response.candidates:
                history.append(response.candidates[0].content)

            return response.text or "The model returned no text."

        if tool_rounds >= MAX_TOOL_ROUNDS:
            logger.warning("Tool round limit reached.")
            return (
                "I couldn't finish within the allowed tool-call "
                "limit. Please try a simpler request."
            )

        tool_rounds += 1

        # Preserve the original Gemini function-call response.
        history.append(response.candidates[0].content)

        tool_responses = []

        for call in function_calls:
            tool = TOOL_REGISTRY.get(call.name)

            if tool is None:
                logger.error(
                    "Rejected unknown tool: %s",
                    call.name,
                )
                return (
                    "Request stopped: an unapproved tool "
                    "was requested."
                )

            try:
                result = tool(**(call.args or {}))

                logger.info(
                    "Tool completed: %s",
                    call.name,
                )

                function_response = types.FunctionResponse(
                    id=call.id,
                    name=call.name,
                    response={"result": result},
                )

            except Exception:
                logger.exception(
                    "Tool execution failed: %s",
                    call.name,
                )

                function_response = types.FunctionResponse(
                    id=call.id,
                    name=call.name,
                    response={
                        "error": "Tool execution failed."
                    },
                )

            tool_responses.append(
                types.Part(
                    function_response=function_response
                )
            )

        history.append(
            types.Content(
                role="user",
                parts=tool_responses,
            )
        )


# ---------- Interactive application ----------

if __name__ == "__main__":
    print("Business AI Assistant")
    print("Type 'exit' to quit.\n")

    conversation_history = []

    while True:
        try:
            question = input("You: ").strip()

            if question.lower() in ("exit", "quit"):
                print("Assistant: Goodbye!")
                break

            if not question:
                continue

            answer = run_agent(
                question,
                conversation_history,
            )

            print(f"\nAssistant: {answer}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nAssistant: Goodbye!")
            break

        except Exception as error:
            # Prints the full traceback in PowerShell
            # and saves it to agent.log.
            logger.exception("Agent request failed")

            # Avoid retaining an incomplete conversation.
            conversation_history.clear()

            print(
                f"\nAssistant error: "
                f"{type(error).__name__}: {error}\n"
            )
