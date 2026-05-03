import requests
import json
import random

class Storyteller:
    """Uses Ollama to generate procedural DM dialogue and challenges."""
    
    def __init__(self, model="llama-3-2-1b-instruct-q4_k_m:latest", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.system_prompt = (
            "You are an N64-era Dungeon Master. Your tone is mysterious and atmospheric. "
            "You are managing a modded Zelda world. Speak to the PLAYER, not the developer. "
            "NEVER ask the user for suggestions or help. "
            "Keep your responses VERY CONCISE (one or two sentences, max 20 words)."
        )

    def generate_dialogue(self, event_type, context=""):
        """Generate dialogue for a specific event."""
        prompts = {
            "intro": "The player has just started their journey. Welcome them.",
            "encounter": f"A random enemy encounter just happened. Context: {context}. Describe it.",
            "boon": "The player received a helpful item or healing. React to it.",
            "curse": "The player was hit by a curse or negative effect. Mock them slightly.",
            "success": "The player completed a difficult challenge. Congratulate them.",
            "fail": "The player failed a challenge. React with disappointment or snark.",
            "idle": "Nothing is happening. Say something mysterious about the world."
        }
        
        prompt = prompts.get(event_type, "Say something DM-like.")
        if context:
            prompt += f" Additional context: {context}"
            
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{self.system_prompt}\n\n{prompt}",
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception as e:
            print(f"[Storyteller] Error: {e}")
            
        # Fallback dialogue
        fallbacks = [
            "The N64 shadows lengthen...",
            "A glitch in the Triforce? No, just your fate.",
            "The crystals hum with ancient power.",
            "I've seen many heroes. Most didn't last this long."
        ]
        return random.choice(fallbacks)

    def generate_challenge_flavor(self, challenge_name, description):
        """Add flavor to an existing challenge."""
        prompt = f"The player is facing a challenge called '{challenge_name}': {description}. Give it a spooky DM introduction."
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{self.system_prompt}\n\n{prompt}",
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception:
            pass
        return f"Behold: {challenge_name}. {description}"
