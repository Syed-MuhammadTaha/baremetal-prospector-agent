import re
import json

class ParserError(Exception):
    """Custom exception raised when the LLM hallucinates or breaks formatting."""
    pass

def parse_llm_output(text: str):
    """
    Parses the LLM's raw text output to extract the Action and Action Input.
    Returns a tuple of (action_name, action_input_dict).
    """
    # 1. Check if the agent has decided it is finished
    if "Final Answer:" in text:
        final_answer = text.split("Final Answer:")[-1].strip()
        return "Final Answer", final_answer

    # 2. Use Regex to find the Action and Action Input
    action_match = re.search(r"Action:\s*(.*?)\n", text)
    action_input_match = re.search(r"Action Input:\s*(.*)", text, re.DOTALL)

    if not action_match or not action_input_match:
        raise ParserError(
            "Could not find 'Action:' or 'Action Input:' in your response. "
            "You MUST use the strict ReAct format."
        )

    action = action_match.group(1).strip()
    action_input_str = action_input_match.group(1).strip()

    # --- THE FIX: ISOLATE THE JSON BLOCK ---
    # Find the first '{' and the last '}' to ignore trailing conversational filler
    start_idx = action_input_str.find('{')
    end_idx = action_input_str.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        action_input_str = action_input_str[start_idx:end_idx + 1]
    # ---------------------------------------

    # 3. Clean up the string (LLMs love to wrap JSON in markdown blocks)
    action_input_str = action_input_str.strip("`").removeprefix("json").strip()

    # 4. Attempt to parse the JSON
    try:
        # json.loads() is strict. It will fail if there are unescaped newlines in the email body.
        # Strict=False allows unescaped control characters (like newlines) inside strings.
        action_input = json.loads(action_input_str, strict=False)
    except json.JSONDecodeError as e:
        raise ParserError(
            f"Your Action Input is not valid JSON. Error: {str(e)}. "
            "If you are writing a multi-line email, you MUST escape newlines with \\n."
        )

    return action, action_input