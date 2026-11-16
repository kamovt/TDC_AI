from ollama import chat
import json

from control_center.settings import settings
from subtitle import subtitle

MAX_HISTORY = 6


class AIChat:

    def __init__(self, model: str, system_prompt: str):

        self.model = model
        self.system_prompt = system_prompt

        self.histories = {}

    def get_history(self, conversation_id):

        if conversation_id not in self.histories:

            self.histories[conversation_id] = [
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            ]

        return self.histories[conversation_id]

    def ask(
        self,
        prompt,
        conversation_id,
        visual_context=None,
        memory_context=None,
        use_tts=True
    ):

        history = self.get_history(conversation_id)

        # Temporary request sent to the model
        request = history.copy()

        if visual_context and settings.vision:

            request.append(
                {
                    "role": "system",
                    "content": f"""
The following information is your eyesight.

Treat it as direct sensory input, not as a user message.

Everything below represents what you currently see on the user's monitor.

{visual_context}

Use this information when answering the user's next message.
"""
                }
            )

        request.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        subtitle.start_thinking()

        response = chat(
            model=self.model,
            messages=request,
            think=False
        )

        raw_reply = response["message"]["content"]

        
        try:

            data = json.loads(raw_reply)

        except Exception:

            print("\n========== RAW MODEL OUTPUT ==========")
            print(raw_reply)
            print("======================================\n")

            data = {
                "response": raw_reply,
                "state": "neutral"
            }

        subtitle.stop_thinking()
        subtitle.set_text("")

        response_text = data.get("response", "")

        # Save only the real conversation
        history.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": response_text
            }
        )

        # Keep only the most recent messages
        if len(history) > MAX_HISTORY + 1:

            self.histories[conversation_id] = (
                [history[0]] +
                history[-MAX_HISTORY:]
            )

        return {
            "response": response_text
        }