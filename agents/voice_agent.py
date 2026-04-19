import json

def run(llm):
    prompt = """
    Generate voice configuration for narration.

    Return ONLY valid JSON:
    {
      "voice": "...",
      "tone": "...",
      "speed": "..."
    }
    """

    response = llm.generate(prompt)

    try:
        return json.loads(response)
    except Exception:
        raise ValueError(f"Invalid JSON from LLM:\n{response}")