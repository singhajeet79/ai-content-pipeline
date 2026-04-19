class MockLLM:
    def generate(self, *args, **kwargs):
        # Normalize prompt
        if len(args) == 1:
            prompt = args[0]
        elif len(args) == 2:
            template, variables = args
            prompt = f"{template} {variables}"
        else:
            prompt = ""

        prompt_lower = prompt.lower()

        # ✅ PRIORITY 1: Scene extraction
        if "break the following script into scenes" in prompt_lower:
            return """[
        {"scene": 1, "text": "Joy sees a river and looks confused."},
        {"scene": 2, "text": "She discovers a wooden bridge."},
        {"scene": 3, "text": "She learns how bridges connect people."}
        ]"""

        # ✅ PRIORITY 2: Topic generation
        if "generate exactly 3 youtube video topics" in prompt_lower:
            return '["Fun Kids Bridge Adventure", "Learning Bridges with Joy", "Why Bridges Matter for Kids"]'
        
        if "generate visual prompts for this scene" in prompt_lower:
            return """{
            "image_prompt": "Pixar style, Joy near a river, soft lighting",
            "video_prompt": "Cinematic pan showing bridge and Joy walking"
            }"""
        
        if "generate voice configuration" in prompt_lower:
            return """{
            "voice": "female",
            "tone": "expressive",
            "speed": "medium"
            }"""        
        
        # ✅ Default
        return f"[MOCK RESPONSE]\n\n{prompt}"

    def generate_json(self, prompt):
        return {
            "name": "Joy",
            "age": 5,
            "description": "Curious child protagonist"
        }