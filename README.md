# Vinci AI Creator

An AI-powered voice assistant running on Raspberry Pi 5.

## Features

- 🎤 Speech recording
- 🗣️ OpenAI Speech-to-Text (ASR)
- 🤖 GPT conversation
- 🔊 OpenAI Text-to-Speech (TTS)
- 💬 Short-term conversation memory
- 🧠 Long-term user memory
- 👁️ Camera image capture
- 🖼️ Image understanding
- 😊 Personalized conversations

---

# Hardware

- Raspberry Pi 5
- Raspberry Pi Camera Module 3
- USB Microphone
- USB Speaker
- HDMI Display (optional)

---

# Software Requirements

- Ubuntu / Raspberry Pi OS
- Python 3.13
- OpenAI API
- python-dotenv

---

# Environment Setup

## 1. Open a terminal

```bash
cd ~/Projects/vinci-ai-robot
```

## 2. Activate the Python virtual environment

```bash
source .venv/bin/activate
```

Verify Python version:

```bash
python --version
```

Expected:

```text
Python 3.13.x
```

---

## 3. Verify OpenAI API Key

Ensure `.env` contains:

```text
OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

# Running Tests

## Test 1 – Audio Recording

```bash
python -m vinci_ai.test_recording
```

Purpose:

- Test microphone recording
- Save recorded audio

---

## Test 2 – Text-to-Speech

```bash
python -m vinci_ai.test_tts
```

Purpose:

- Generate speech
- Play through speaker

---

## Test 3 – Speech Recognition

```bash
python -m vinci_ai.test_asr
```

Purpose:

- Record audio
- Send to OpenAI ASR
- Print recognized text

---

## Test 4 – Camera

```bash
python -m vinci_ai.test_camera
```

Purpose:

- Capture image from Camera Module 3

---

## Test 5 – Vision

```bash
python -m vinci_ai.test_vision
```

Purpose:

- Capture image
- Send image to GPT
- Print image description

---

## Test 6 – End-to-End Voice Assistant

```bash
python -m vinci_ai.test_voice_chat
```

Purpose:

Complete voice conversation pipeline.

```
Microphone
    ↓
Audio Recorder
    ↓
OpenAI ASR
    ↓
Conversation History
    ↓
Long-Term Memory
    ↓
GPT-4o-mini
    ↓
OpenAI TTS
    ↓
USB Speaker
```

---

# Project Structure

```
vinci_ai/
├── audio/
├── config/
├── llm/
├── prompts/
├── tts/
├── vision/
├── memory_store.py
├── robot.py
├── voice_assistant.py
└── test_voice_chat.py
```

---

# Current Project Status

Current milestone:

**v0.3.0**

Implemented:

- ✅ Voice conversation
- ✅ Camera vision
- ✅ Image understanding
- ✅ Conversation history
- ✅ Long-term memory
- ✅ Personalized responses
- ✅ Modular architecture

Future work:

- Robot body
- Emotion/personality improvements
- Faster response latency
- Wake-word detection
- Continuous conversation
- Two AI robots talking to each other