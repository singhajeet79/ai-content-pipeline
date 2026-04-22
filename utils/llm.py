import os
import json
import requests

from dotenv import load_dotenv

# Explicitly load the .env file from the current directory
load_dotenv()

# ---------------------------
# LAZY IMPORT HANDLER
# ---------------------------
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from google import genai
except ImportError:
    genai = None

# ---------------------------
# MOCK LLM (FULLY COMPATIBLE)
# ---------------------------
class MockLLM:
    """
    Deterministic fallback LLM.
    Always returns schema-compliant outputs so pipeline never breaks.
    """

    # -----------------------
    # TEXT GENERATION
    # -----------------------
    def generate(self, prompt: str) -> str:
        p = (prompt or "").lower()

        if "topic" in p:
            return '["Mock Topic 1", "Mock Topic 2", "Mock Topic 3"]'

        if "script" in p:
            return (
                "Once upon a time, there was a curious child who discovered "
                "something magical and learned an important life lesson."
            )

        if "scene" in p:
            return '[{"scene": 1, "text": "A calm opening scene."}]'

        if "visual" in p:
            return '{"image_prompt": "A simple mock image", "video_prompt": "A simple mock video"}'

        if "voice" in p:
            return '{"voice": "neutral", "tone": "calm", "speed": "medium"}'

        # default safe fallback
        return '{"message": "mock"}'

    # -----------------------
    # JSON GENERATION (CRITICAL)
    # -----------------------
    def generate_json(self, prompt: str):
        p = (prompt or "").lower()

        # TOPIC
        if "topic" in p:
            return ["Mock Topic 1", "Mock Topic 2", "Mock Topic 3"]

        # CHARACTER
        if "character" in p:
            return {
                "name": "Mock Character",
                "description": "A simple test character",
                "traits": ["curious", "brave"]
            }

        # SCENES
        if "scene" in p:
            return [
                {"scene": 1, "text": "A calm opening scene."},
                {"scene": 2, "text": "Something interesting happens."}
            ]

        # VISUAL
        if "visual" in p:
            return {
                "image_prompt": "Mock image prompt",
                "video_prompt": "Mock video prompt"
            }

        # VOICE
        if "voice" in p:
            return {
                "voice": "neutral",
                "tone": "calm",
                "speed": "medium"
            }

        # SCRIPT (if ever routed here)
        if "script" in p:
            return {
                "text": "Mock script content"
            }

        # DEFAULT SAFE FALLBACK
        return {
            "message": "mock"
        }

# ---------------------------
# OPENROUTER LLM
# ---------------------------
class OpenRouterLLM:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key: raise RuntimeError("OPENROUTER_API_KEY not set")
        self.model = "google/gemma-3-4b-it:free"
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def _request(self, prompt, sys_msg):
        # Merge system message into user content for better compatibility
        combined_content = f"Instruction: {sys_msg}\n\nPrompt: {prompt}"
        
        response = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": combined_content} # No more "system" role
                ],
                "temperature": 0.5
            }
        )
        if response.status_code != 200: 
            raise RuntimeError(f"OpenRouter Error: {response.text}")
        return response.json()["choices"][0]["message"]["content"]

    def generate(self, prompt: str) -> str:
        return self._request(prompt, "Follow instructions strictly.")

    def generate_json(self, prompt: str) -> dict:
        content = self._request(prompt, "Return ONLY valid JSON.")
        return json.loads(content)

# ---------------------------
# OPENAI LLM
# ---------------------------
class OpenAILLM:
    def __init__(self):
        if not OpenAI: raise ImportError("openai library not installed.")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "deepseek/deepseek-chat:free"

    def generate(self, prompt: str) -> str:
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()

    def generate_json(self, prompt: str) -> dict:
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)

# ---------------------------
# GEMINI LLM (With Schema Healing)
# ---------------------------
class GeminiLLM:
    def __init__(self):
        if not genai: raise ImportError("google-genai not installed.")
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1'}
        )
        self.model = "models/gemini-2.5-flash"

    def generate(self, prompt: str) -> str:
        return self.client.models.generate_content(model=self.model, contents=prompt).text.strip()

    def generate_json(self, prompt: str) -> dict:
        instruction = f"{prompt}\n\nIMPORTANT: Return ONLY raw JSON. No markdown."
        response = self.client.models.generate_content(model=self.model, contents=instruction)
        text = response.text.strip()

        # Clean Markdown
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        
        data = json.loads(text.strip())

        # --- HEALING LOGIC ---
        if "description" not in data:
            data["description"] = data.pop("outfit", data.pop("bio", "Character description."))
        if "age" in data and isinstance(data["age"], str):
            digits = "".join(filter(str.isdigit, data["age"]))
            data["age"] = int(digits) if digits else 0
            
        return data

# ---------------------------
# RESILIENCE & FACTORY
# ---------------------------
class ResilientLLM:
    def __init__(self, primary_llm):
        self.primary = primary_llm
        self._fallback = None
        self._final_fallback = MockLLM()   # ✅ NEW

    def _get_fallback(self):
        if not self._fallback:
            self._fallback = OpenRouterLLM()
        return self._fallback

    def generate(self, prompt):
        try:
            return self.primary.generate(prompt)

        except Exception as e:
            print(f"⚠️ Primary LLM failed: {e}. Trying fallback...")

            try:
                return self._get_fallback().generate(prompt)

            except Exception as e2:
                print(f"⚠️ Fallback LLM failed: {e2}. Using MockLLM...")

                return self._final_fallback.generate(prompt)   # ✅ GUARANTEED

    def generate_json(self, prompt):
        try:
            return self.primary.generate_json(prompt)

        except Exception as e:
            print(f"⚠️ Primary JSON failed: {e}. Trying fallback...")

            try:
                return self._get_fallback().generate_json(prompt)

            except Exception as e2:
                print(f"⚠️ Fallback JSON failed: {e2}. Using MockLLM...")

                return self._final_fallback.generate_json(prompt)  # ✅ GUARANTEED
def get_llm(config):
    provider = config.get("llm_provider", "gemini")

    try:
        if provider == "gemini":
            return ResilientLLM(GeminiLLM())

        if provider == "openai":
            return ResilientLLM(OpenAILLM())

        if provider == "openrouter":
            return ResilientLLM(OpenRouterLLM())

    except Exception as e:
        print(f"❌ LLM Init Failed: {e}")

    return MockLLM()