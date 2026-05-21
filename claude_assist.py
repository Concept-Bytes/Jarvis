"""
Claude-powered drop-in replacement for assist.py.
Used by jarvis.py (CLI voice mode). The web interface uses app.py instead.
"""
import anthropic
import asyncio
import io
import os

from pygame import mixer

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
mixer.init()

conversation_history = []

SYSTEM_PROMPT = (
    "You are Jarvis, a voice-activated personal AI assistant. Be natural and concise. "
    "If you need to trigger a device tool, append a #command at the very end of your response."
)


def ask_question_memory(question: str) -> str:
    conversation_history.append({"role": "user", "content": question})
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=conversation_history,
    )
    reply = response.content[0].text
    conversation_history.append({"role": "assistant", "content": reply})
    return reply


async def _tts_async(text: str) -> bytes:
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
        audio = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]
        return audio
    except ImportError:
        print("edge-tts not installed. Run: pip install edge-tts")
        return b""


def TTS(text: str) -> str:
    audio_data = asyncio.run(_tts_async(text))
    if audio_data:
        sound = mixer.Sound(io.BytesIO(audio_data))
        sound.play()
        while mixer.get_busy():
            import pygame
            pygame.time.wait(100)
    return "done"
