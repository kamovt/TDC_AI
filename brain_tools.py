import os
import json
from ollama import chat
from threading import Thread


from chat import AIChat
from control_center.settings import settings

PERSONALITY_MODEL = "qwen3.5:9b"
VISION_MODEL = "qwen3.5:9b"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

SYSTEM_PROMPT = os.path.join(
    BASE_DIR,
    "prompts",
    "system.txt"
)


with open(
    SYSTEM_PROMPT,
    "r",
    encoding="utf-8"
) as f:
    system_prompt = f.read()

ai = AIChat(
    model=PERSONALITY_MODEL,
    system_prompt=system_prompt
)

def load_prompt(filename: str) -> str:
    with open(
        os.path.join(PROMPTS_DIR, filename),
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()


def ask_model(
    model: str,
    system_prompt: str,
    user_prompt: str,
    image_path: str = None,
    format=None,
):

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    user_message = {
        "role": "user",
        "content": user_prompt
    }

    if image_path:
        user_message["images"] = [image_path]

    messages.append(user_message)

    response = chat(
        model=model,
        messages=messages,
        format=format,
        think=False
    )

    return response["message"]["content"]


def describe_screen(image_path: str):
    if not settings.vision:
        return ""
    
    return ask_model(
        model=VISION_MODEL,
        system_prompt=load_prompt("vision.txt"),
        user_prompt="Describe this screen.",
        image_path=image_path
    )
