from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import sys
import requests
import uuid
import threading

app = Flask(__name__)
CORS(app)

# ── TTS Setup ──────────────────────────────────────────────────────────────────
TTS_ENABLED   = False
tts_engine    = None
tts_lock      = threading.Lock()
TTS_AUDIO_DIR = "tts_audio"
os.makedirs(TTS_AUDIO_DIR, exist_ok=True)

def safe_print(msg):
    """Print without crashing on Windows terminals that can't handle Unicode."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

def init_tts():
    global tts_engine, TTS_ENABLED

    # ------------------------------------------------------------------ #
    # CRITICAL: pyttsx3 on Windows uses COM and segfaults when Flask's    #
    # reloader spawns a child process. We must only init TTS in the MAIN  #
    # worker process, not in the reloader watcher process.                #
    # Flask sets WERKZEUG_RUN_MAIN=true in the real worker process.       #
    # ------------------------------------------------------------------ #
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        safe_print("DEBUG: Skipping TTS init in reloader process")
        return

    try:
        import pyttsx3
        engine = pyttsx3.init()

        voices = engine.getProperty('voices')
        chosen = None
        for v in voices:
            name_lower = v.name.lower()
            if 'zira' in name_lower or 'hazel' in name_lower:
                chosen = v
                break
        if not chosen and voices:
            # fallback: first available voice
            chosen = voices[0]

        if chosen:
            engine.setProperty('voice', chosen.id)
            safe_print(f"DEBUG: TTS voice -> {chosen.name}")

        engine.setProperty('rate',   165)
        engine.setProperty('volume', 1.0)

        tts_engine  = engine
        TTS_ENABLED = True
        safe_print("DEBUG: pyttsx3 TTS ready")

    except ImportError:
        safe_print("WARNING: pyttsx3 not installed. Run: pip install pyttsx3")
    except Exception as e:
        safe_print(f"WARNING: TTS init failed: {e}")

threading.Thread(target=init_tts, daemon=True).start()


def generate_audio(text: str):
    if not TTS_ENABLED or tts_engine is None:
        return None
    try:
        filename = f"{uuid.uuid4().hex}.wav"
        filepath = os.path.join(TTS_AUDIO_DIR, filename)

        with tts_lock:
            tts_engine.save_to_file(text, filepath)
            tts_engine.runAndWait()

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            safe_print(f"DEBUG: Audio saved -> {filepath} ({os.path.getsize(filepath)} bytes)")
            return f"/audio/{filename}"
        else:
            safe_print("ERROR: Audio file empty or missing after generation")
            return None

    except Exception as e:
        safe_print(f"ERROR: TTS generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ── Conversation ───────────────────────────────────────────────────────────────
conversation_sessions = {}

SYSTEM_PROMPT = """You are a compassionate and intelligent support assistant for students balancing work and studies.

Your purpose is to:
- Listen with empathy and understand their struggles
- Provide thoughtful, personalized advice based on their specific situation
- Help them develop strategies for work-life balance
- Offer emotional support and encouragement
- Answer any questions they have

Be warm, conversational, and genuine. Adapt your tone to their needs.
Give practical, actionable advice tailored to what they're dealing with.
Keep responses concise but meaningful (2-4 sentences usually).
You can help with anything - academics, work stress, personal issues, mental health, time management, or just listening."""


def get_ai_response(user_message, conversation_history, api_key):
    if not api_key:
        return "I need an API key to respond. Please provide it in the GUI."
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.8
        }
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers, json=payload, timeout=20
        )
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content'].strip()
        safe_print(f"ERROR: Groq {response.status_code}: {response.text}")
        return f"API Error: {response.status_code}"

    except Exception as e:
        safe_print(f"ERROR: {e}")
        return f"Error: {str(e)}"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/audio/<filename>')
def serve_audio(filename):
    filepath = os.path.join(TTS_AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    return send_file(filepath, mimetype='audio/wav')


@app.route('/tts-status')
def tts_status():
    return jsonify({'enabled': TTS_ENABLED})


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data          = request.json
        user_message  = data.get('message', '').strip()
        session_id    = data.get('session_id', 'default')
        tts_requested = data.get('tts', True)
        api_key       = data.get('api_key', '').strip()

        if not user_message:
            return jsonify({'error': 'Please enter a message'}), 400

        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []

        bot_response = get_ai_response(user_message, conversation_sessions[session_id], api_key)

        audio_url = None
        if tts_requested and TTS_ENABLED:
            audio_url = generate_audio(bot_response)
            safe_print(f"DEBUG: audio_url = {audio_url}")

        conversation_sessions[session_id].append({'role': 'user',      'content': user_message})
        conversation_sessions[session_id].append({'role': 'assistant', 'content': bot_response})

        return jsonify({
            'response':    bot_response,
            'audio_url':   audio_url,
            'tts_enabled': TTS_ENABLED
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # use_reloader=False stops Flask from spawning a second process,
    # which is what caused the pyttsx3 COM segfault on Windows.
    app.run(debug=True, port=5000, use_reloader=False)
