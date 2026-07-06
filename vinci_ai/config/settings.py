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