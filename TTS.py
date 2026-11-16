
import os
import re
import html
import queue
import asyncio
import tempfile
import threading

import time
import edge_tts
import pygame

from subtitle import subtitle
from control_center.settings import settings
from speech.audio_state import TTS_PLAYING

try:
    pygame.mixer.init(
        frequency=44100,
        size=-16,
        channels=2,
        buffer=1024
    )
    print("Audio mixer initialized successfully.")

except pygame.error as e:
    print(f"Audio initialization failed: {e}")
    
# =========================
# CONFIGURATION
# =========================

VOICE = "pt-BR-FranciscaNeural"

print(f"Using Edge TTS: {VOICE}")

tts_queue = queue.Queue()

queue_lock = threading.Lock()
shutdown_requested = False


# =========================
# TEXT CLEANING
# =========================

def clean_for_tts(text):

    # Remove HTML tags
    text = re.sub(r"<[^>]*>", "", text)

    # Decode HTML entities
    text = html.unescape(text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================
# AUDIO GENERATION
# =========================

async def generate_audio(text, path):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE
    )

    await communicate.save(path)


def generate_wav(text):
    """
    Generate Portuguese speech using Edge TTS.
    Returns an MP3 temporary file.
    """

    temp = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    )

    temp_path = temp.name
    temp.close()

    try:

        asyncio.run(
            generate_audio(text, temp_path)
        )

        return temp_path

    except Exception:

        if os.path.exists(temp_path):
            os.remove(temp_path)

        raise


# =========================
# TTS WORKER
# =========================

def tts_worker():

    while True:

        text = tts_queue.get()

        temp_path = None

        try:

            if text is None:
                return

            if not settings.tts:
                continue

            text = clean_for_tts(text)

            if not text:
                continue

            print("Generating Portuguese speech...")

            # Generate complete response
            temp_path = generate_wav(text)

            # Show complete subtitle while speaking
            subtitle.set_text(text)

            # Play complete audio
            TTS_PLAYING.set()

            try:
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)

                pygame.mixer.music.unload()

                # Give the microphone time to stop receiving speaker audio.
                time.sleep(0.5)

            finally:
                TTS_PLAYING.clear()

            subtitle.set_text("")

            print("Speech finished.")

        except Exception as e:

            print(f"TTS Error: {e}")

            subtitle.set_text("")

        finally:

            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            tts_queue.task_done()


# =========================
# START WORKER
# =========================

worker = threading.Thread(
    target=tts_worker,
    daemon=True
)

worker.start()


# =========================
# SPEAK
# =========================

def speak(text: str):

    global shutdown_requested

    if not settings.tts:
        return

    if not text or not text.strip():
        return

    text = clean_for_tts(text)

    if not text:
        return

    with queue_lock:

        if shutdown_requested:
            return

        tts_queue.put(text)

# =========================
# WAIT
# =========================

def wait_until_done():
    """
    Wait until the current and pending speech finish.
    """

    tts_queue.join()


# =========================
# SHUTDOWN
# =========================

def shutdown():
    """
    Stop the TTS worker cleanly.
    """

    global shutdown_requested

    with queue_lock:

        if shutdown_requested:
            return

        shutdown_requested = True

        # Discard pending speech
        while True:

            try:
                tts_queue.get_nowait()
                tts_queue.task_done()

            except queue.Empty:
                break

        tts_queue.put_nowait(None)
