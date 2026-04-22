def extract_character_profile(script, llm):
    prompt = f"""
Extract the MAIN character from the script.

Return ONLY valid JSON. No explanation.

Schema:
{{
  "name": string,
  "age": number,
  "description": string
}}

Rules:
- description MUST summarize the character in 1–2 sentences
- age MUST be a number (not string, not empty)
- If age is unknown, estimate a reasonable value
- DO NOT include extra fields (no face_structure, outfit, etc.)
- DO NOT return partial or invalid JSON

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