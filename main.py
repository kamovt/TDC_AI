import os
from threading import Thread
import keyboard
from subtitle import subtitle
import re
import asyncio
import concurrent
import time

print("Starting AI...")
from TTS import speak

from brain_tools import ai
print("Chat module loaded.")

from speech import SpeechRecognizer
print("Voice Recognition loaded")

from vision import analyze_screen
print("Vision module loaded")

from control_center.control_center import cclaunch
from control_center.settings import settings

cclaunch()

print("Settings loaded")

from subtitle import subtitle
print("Subtitles loaded")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Project folder:", BASE_DIR)


PROMPT_FILE = os.path.join(
    BASE_DIR,
    "prompts",
    "system.txt"
)

print("Prompt file:", PROMPT_FILE)


with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    system_prompt = f.read()

print("System prompt loaded.")

recognizer = SpeechRecognizer()

print("AI initialized.")


print("\nAI is online.")
print("Type 'quit' to exit.\n")

DISCORD_VOICE_MODE = True
def shutdown():
    print("\nCtrl+Shift+D pressed. Shutting down AI...")

    os._exit(0)

keyboard.add_hotkey(
    "ctrl+shift+d",
    shutdown
)

while True:

    def userinput():
        while True:

            if settings.VOICE_MODE:
                user_input = recognizer.listen()

                if user_input:
                    print(f"\nYou: {user_input}")
                    return user_input

                continue

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(input, "You: ")

                while not future.done():

                    time.sleep(0.1)

                    if settings.VOICE_MODE:
                        break

                if settings.VOICE_MODE:
                    continue

                return future.result()
            
    user_input = userinput()

    if user_input.lower() == "quit":
        break
    
    visual_context = analyze_screen()

    print("\n===== VISION =====")
    print(visual_context)
    print("==================\n")


    prompt=f"""
    Platform: Local
    Julius: {user_input}
    """

    result = ai.ask(
        prompt=user_input,
        conversation_id="local",
        visual_context=visual_context
    )

    response = result["response"]

    print(f"\nAI: {response}\n")

    conversation = f"""
    User:
    {user_input}

    Lumina:
    {response}
    """

    buffer = response

    while True:
        match = re.search(r"[.!?]\s", buffer)

        if not match:
            break

        sentence = buffer[:match.end()].strip()

        if sentence:
            subtitle.set_text(sentence)
            speak(sentence)

        buffer = buffer[match.end():]

    if buffer.strip():
        subtitle.set_text(buffer.strip())
        speak(buffer.strip())
