from jsonschema import validate, ValidationError


# ---------------------------
# SCHEMAS
# ---------------------------

TOPIC_SCHEMA = {
    "type": "array",
    "items": {"type": "string"}
}

SCRIPT_SCHEMA = {
    "type": "string"
}

CHARACTER_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
        "description": {"type": "string"}
    },
    "required": ["name", "age", "description"]
}

SCENE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "scene": {"type": "number"},
            "text": {"type": "string"}
        },
        "required": ["scene", "text"]
    }
}

VISUAL_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "image_prompt": {"type": "string"},
            "video_prompt": {"type": "string"}
        },
        "required": ["image_prompt", "video_prompt"]
    }
}

VOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "voice": {"type": "string"},
        "speed": {
            "type": "string",
            "enum": ["slow", "medium", "fast"]
        }
    },
    "required": ["voice", "speed"]
}


# ---------------------------
# VALIDATOR
# ---------------------------

def validate_schema(data, schema, agent_name):
    try:
        validate(instance=data, schema=schema)
        print(f"✅ {agent_name} schema validated")
    except ValidationError as e:
        raise Exception(
            f"❌ {agent_name} schema validation failed:\n{e.message}"
        )