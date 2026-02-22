# 🎓 Study-Work Balance Support Bot

A compassionate AI chatbot designed to help students navigate the challenges of balancing work and studies. Features real-time AI responses powered by Groq, and text-to-speech with fully customisable voice settings.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 💬 **AI-powered chat** — empathetic responses via Groq (Llama 3.1)
- 🔊 **Text-to-speech** — browser Web Speech API with customisable voice, speed, and pitch
- 🎛 **Voice settings panel** — pick any installed voice, adjust speed/pitch/volume, test live
- 💾 **Voice preferences saved** — settings persist between sessions via localStorage
- 🗂 **Conversation memory** — remembers last 10 messages for context
- ⚡ **Fast** — Groq inference is extremely quick (~1s responses)

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/study-balance-bot.git
cd study-balance-bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Get a free Groq API key at [console.groq.com](https://console.groq.com)

```bash
# Copy the example file
cp .env.example .env

# Then edit .env and add your key:
# GROQ_API_KEY=your_key_here
```

### 5. Run the app

```bash
python chatbot.py
```

Open your browser and go to **http://localhost:5000**

---

## 🎛 Voice Customisation

Click the **🎛 Voice Settings** button in the header to customise:

| Setting | Range | Tips |
|---------|-------|------|
| **Voice** | All installed English voices | Try Microsoft Jenny (Online) for best quality |
| **Speed** | 0.5× – 2.0× | ~0.85× feels more natural and relaxed |
| **Pitch** | 0.5 – 2.0 | ~0.9 sounds warmer, less robotic |
| **Volume** | 0% – 100% | — |

Use the **▶ Test Voice** button to hear changes instantly.

---

## 🗂 Project Structure

```
study-balance-bot/
├── chatbot.py        # Flask backend + Groq AI + pyttsx3 TTS
├── index.html        # Frontend UI with voice settings
├── requirements.txt  # Python dependencies
├── .env.example      # API key template
├── .gitignore        # Ignores .env and tts_audio/
└── README.md         # This file
```

---

## 🔧 How It Works

```
User types message
       ↓
Frontend sends POST /chat to Flask
       ↓
Flask calls Groq API (Llama 3.1-8b-instant)
       ↓
Response text returned to frontend
       ↓
Browser Web Speech API reads it aloud
(with your chosen voice & settings)
```

**TTS Architecture:** The app uses the browser's built-in Web Speech API as the primary TTS engine — this means zero extra downloads and it works immediately. The backend also supports pyttsx3 as a secondary option (generates WAV files served via `/audio/`), which the frontend will use automatically if the backend TTS is ready.

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, Flask-CORS |
| AI | Groq API (Llama 3.1 8B Instant) |
| Frontend | Vanilla HTML/CSS/JS |
| TTS (primary) | Web Speech API (browser built-in) |
| TTS (secondary) | pyttsx3 (Windows/Mac/Linux native voices) |

---

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key from console.groq.com | ✅ Yes |

---


*Built with ❤️ to help students find balance*
