import openai

from config import GROQ_API_KEY, GROQ_BASE_URL, MODEL

# One shared underlying client so the HTTP connection pool is reused everywhere.
_client = openai.OpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)


class LLM:
    """Thin wrapper around `client.chat.completions.create`.

    The model is fixed to `config.MODEL` (llama-3.1-8b-instant) and is never
    passed in by callers. Per-purpose default parameters (e.g. `stop`) are set
    once at construction and merged into every call; per-call kwargs override
    those defaults.
    """

    def __init__(self, **default_params):
        self._default_params = default_params

    def complete(self, messages, **overrides):
        """Create a chat completion. `overrides` win over init defaults."""
        params = {**self._default_params, **overrides}
        return _client.chat.completions.create(
            model=MODEL,
            messages=messages,
            **params,
        )


# Configured once per use-case — no shared mutable state, no default leakage.
agent_llm = LLM(stop=["Observation:"])  # ReAct loop in engine.py
summary_llm = LLM()                     # memory compression in memory.py
