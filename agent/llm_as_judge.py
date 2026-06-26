import json
from .llm import agent_llm
from .prompt import JUDGE_SYSTEM_PROMPT

def evaluate_email(email_text: str) -> dict:
    """Passes the drafted email to the LLM Judge for scoring."""
    
    messages = [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": f"EVALUATE THIS DRAFT:\n\n{email_text}"}
    ]
    
    try:
        response = agent_llm.complete(messages)
        
        content = response.choices[0].message.content
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx + 1]
            return json.loads(json_str, strict=False)
        else:
            return {"score": 0, "feedback": "Judge failed to return JSON.", "passed": False}
            
    except Exception as e:
        return {"score": 0, "feedback": f"Evaluation error: {str(e)}", "passed": False}