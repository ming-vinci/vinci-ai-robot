from dotenv import load_dotenv
import os

load_dotenv()

# =========================
# OpenAI
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# =========================
# LLM
# =========================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5")


# =========================
# ASR
# =========================

ASR_PROVIDER = os.getenv("ASR_PROVIDER", "openai")
ASR_MODEL = os.getenv("ASR_MODEL", "gpt-4o-mini-transcribe")
ASR_LANGUAGE = os.getenv("ASR_LANGUAGE", "en")


# =========================
# TTS
# =========================

TTS_PROVIDER = os.getenv("TTS_PROVIDER", "openai")
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "alloy")


# =========================
# AUDIO OUTPUT
# =========================

AUDIO_OUTPUT_DEVICE = os.getenv("AUDIO_OUTPUT_DEVICE", "plughw:0,0")  # Default to the first available audio output device