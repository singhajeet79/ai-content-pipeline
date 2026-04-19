import json

def run(config, llm):
    genre = ", ".join(config.get("genre", []))
    tone = ", ".join(config.get("tone", []))
    language = config.get("language", "English")
    content_type = config.get("content_type", "General")
    audience = config.get("audience", "General")

    prompt = f"""
    Generate exactly 3 YouTube video topics.

    Content Type: {content_type}
    Audience: {audience}
    Genre: {genre}
    Tone: {tone}
    Language: {language}

    Return ONLY valid JSON in this format:
    ["topic 1", "topic 2", "topic 3"]
    """

    response = llm.generate(prompt)

    try:
        return json.loads(response)
    except Exception:
        raise ValueError(f"Invalid JSON from LLM:\n{response}")