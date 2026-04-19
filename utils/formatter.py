import json

def safe_parse_json(text):

    if not text or not text.strip():
        raise ValueError("Empty response from LLM")

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        print("⚠️ Invalid JSON. Attempting fix...")

        # basic cleanup
        cleaned = text.strip()

        # remove backticks if LLM adds them later
        cleaned = cleaned.replace("```json", "").replace("```", "")

        try:
            return json.loads(cleaned)
        except:
            raise ValueError(f"JSON parsing failed. Raw output:\n{cleaned}")