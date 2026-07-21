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
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini") # gpt-5


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
TTS_VOICE = os.getenv("TTS_VOICE", "alloy") # alloy and shimmer are male, coral and nova are female
TTS_STYLE = os.getenv(
    "TTS_STYLE",
    (
        "Speak as a cute, cheerful, youthful animated companion. "
        "Use a light, bright voice, playful rhythm, expressive intonation, "
        "and a slightly higher pitch. Sound energetic and friendly. "
        "Do not sound deep, serious, mature, or formal."
    ),
)


# =========================
# AUDIO INPUT
# =========================

AUDIO_INPUT_DEVICE = os.getenv(
    "AUDIO_INPUT_DEVICE",
    "plughw:2,0",
)

AUDIO_INPUT_DEVICE_INDEX = int(
    os.getenv(
        "AUDIO_INPUT_DEVICE_INDEX",
        "0",
    )
)

AUDIO_SAMPLE_RATE = int(
    os.getenv(
        "AUDIO_SAMPLE_RATE",
        "16000",
    )
)

AUDIO_SILENCE_THRESHOLD = float(
    os.getenv("AUDIO_SILENCE_THRESHOLD", "500")
)

AUDIO_SILENCE_DURATION = float(
    os.getenv("AUDIO_SILENCE_DURATION", "1.0")
)

AUDIO_MAX_RECORD_SECONDS = float(
    os.getenv("AUDIO_MAX_RECORD_SECONDS", "10.0")
)


# =========================
# AUDIO OUTPUT
# =========================

AUDIO_OUTPUT_DEVICE = os.getenv("AUDIO_OUTPUT_DEVICE", "plughw:3,0")  # The USB speaker


# =========================
# LONG TERM MEMORY
# =========================

ENABLE_LONG_TERM_MEMORY_UPDATE = (
    os.getenv("ENABLE_LONG_TERM_MEMORY_UPDATE", "true").lower()
    == "true"
)


# =========================
# VISION / CAMERA
# =========================

CAMERA_PROVIDER = os.getenv(
    "CAMERA_PROVIDER",
    "usb",
)

CAMERA_OUTPUT_DIRECTORY = os.getenv(
    "CAMERA_OUTPUT_DIRECTORY",
    "data/images",
)

USB_CAMERA_INDEX = int(os.getenv("USB_CAMERA_INDEX", "8"))