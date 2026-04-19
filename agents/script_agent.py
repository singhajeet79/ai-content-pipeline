def extract_character_profile(script, llm):
    prompt = f"""
    Extract main character details from this script.

    Return JSON:
    {{
      "name": "",
      "age": "",
      "face_structure": "",
      "skin_tone": "",
      "hair_style": "",
      "outfit": ""
    }}

    Script:
    {script}
    """

    return llm.generate_json(prompt)


def run(config, llm):
    topic = config.get("topic")

    tone = ", ".join(config.get("tone", []))
    language = config.get("language", "English")
    content_type = config.get("content_type", "Story")
    audience = config.get("audience", "General")

    # ✅ NEW: duration control (added, not replacing anything)
    duration = config.get("duration_minutes", 1)
    char_per_min = config.get("char_per_min", 800)
    target_length = duration * char_per_min

    prompt = f"""
    Write a YouTube script.

    Topic: {topic}
    Content Type: {content_type}
    Audience: {audience}
    Tone: {tone}
    Language: {language}

    Target length: {target_length} characters

    Keep it engaging and suitable for the audience.
    """

    response = llm.generate(prompt)

    return response