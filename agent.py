
from tools import calculate


# Our available tools
TOOLS = {
    "calculate": calculate,
}


def run_tool(tool_name, arguments):
    """Find a tool by name and execute it."""

    tool = TOOLS.get(tool_name)

    if tool is None:
        return f"Unknown tool: {tool_name}"

    try:
        return tool(**arguments)
    except Exception as error:
        return f"Tool error: {error}"


def run_agent(user_input):
    print(f"User: {user_input}")

    # Fake model decision for now.
    tool_name = "calculate"
    arguments = {
        "expression": "157 * 246"
    }

    print(f"Agent: I want to use '{tool_name}'")
    print(f"Agent -> Tool: {arguments}")

    result = run_tool(tool_name, arguments)

    print(f"Tool -> Agent: {result}")

    return f"The answer is {result}."


if __name__ == "__main__":
    answer = run_agent("Calculate 157 * 246")

    print(f"Agent: {answer}")
