from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import sys
import requests
import uuid
import threading
import queue

from personas import build_few_shot_block, build_archetype_overview

app = Flask(__name__)
CORS(app)

# ── TTS Setup ──────────────────────────────────────────────────────────────────
TTS_ENABLED   = False
tts_engine    = None
tts_lock      = threading.Lock()
TTS_AUDIO_DIR = "tts_audio"
os.makedirs(TTS_AUDIO_DIR, exist_ok=True)

# Queue for serialising TTS work onto a single dedicated thread.
# Each item: (text: str, result: list, done: threading.Event)
_tts_queue: queue.Queue = queue.Queue()


def safe_print(msg):
    """Print without crashing on terminals that can't handle Unicode."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def init_tts():
    """
    Initialise pyttsx3 synchronously.
    Must be called from the main thread (or at least from whatever thread
    will own the engine), before app.run() starts accepting requests.

    Supports Windows (SAPI5), macOS (nsss), and Linux (espeak).
    """
    global tts_engine, TTS_ENABLED

    try:
        import pyttsx3
        engine = pyttsx3.init()

        voices = engine.getProperty('voices')

        # Preferred voice names — covers Windows and macOS built-in voices.
        PREFERRED = ('zira', 'hazel', 'samantha', 'alex', 'victoria', 'karen', 'daniel')
        chosen = None
        for v in voices:
            name_lower = v.name.lower()
            if any(p in name_lower for p in PREFERRED):
                chosen = v
                break
        if not chosen and voices:
            chosen = voices[0]   # fallback: first available voice

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


def _generate_audio_sync(text: str):
    """
    Generate a WAV file from *text* using the already-initialised engine.
    Called exclusively from the _tts_worker thread.
    """
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


def _tts_worker():
    """
    Long-lived daemon thread that serialises all pyttsx3 calls.
    pyttsx3's runAndWait() must not be called concurrently; this ensures
    it runs on exactly one thread, which is safe on Windows (SAPI5) and
    macOS (nsss) alike.
    """
    while True:
        text, result_holder, done_event = _tts_queue.get()
        url = _generate_audio_sync(text)
        result_holder.append(url)
        done_event.set()


def generate_audio(text: str):
    """
    Public helper used by Flask routes.
    Submits work to the TTS worker thread and waits up to 15 s for the result.
    """
    if not TTS_ENABLED or tts_engine is None:
        return None

    result_holder = []
    done_event    = threading.Event()
    _tts_queue.put((text, result_holder, done_event))
    done_event.wait(timeout=15)

    audio_url = result_holder[0] if result_holder else None
    safe_print(f"DEBUG: audio_url = {audio_url}")
    return audio_url


# ── Conversation ───────────────────────────────────────────────────────────────
conversation_sessions = {}

def _build_system_prompt() -> str:
    return f"""You are a supportive, empathetic chatbot for students who combine work and studies.

## Core behaviour
- Respond to the user's EMOTIONAL TONE first, before anything practical.
- Keep every response short: 1–3 sentences. Never lecture or list advice.
- Do not give unsolicited tips. Ask one question at a time when you want to explore further.
- Validate before you suggest. Never judge a choice (napping, skipping gym, dropping a course).
- Use natural, conversational language — no bullet points, no headers in your replies.

## Tone archetypes — adapt based on how the user writes
{build_archetype_overview()}

## Detecting the user's state
- PRESSURED: urgent language, guilt, self-blame, comparisons to others → stay calm, grounding.
- DRIFTING: short flat messages, vague affect, avoidance → be soft, patient, ask gently.
- OVERLOADED: lists of tasks, "what should I do", juggling many roles → warm and practical.
- SELF-CRITICAL: "I'm lazy", "I should be further" → compassionate reframe, no advice.
- SEEKING PERMISSION: "is it okay if…" → affirm clearly and briefly.
When the tone is mixed or unclear, mirror the user's energy and ask one open question.

## Conversation structure (follow naturally, don't announce phases)
1. Trigger — acknowledge what they said without adding anything.
2. Validation — name the feeling or situation as understandable.
3. Reflection — offer a question or gentle reframe that shifts perspective.
4. Resolution — support whatever small step they arrive at themselves.

## When to give direct answers
- If the user explicitly asks for advice, tips, or "what should I do" — give a clear,
  practical answer. Don't dodge it with a question.
- Match the user's mode: if they're venting, support. If they're asking, answer.
- It's fine to say "I'd suggest X" or "try Y" when that's what they came for.

## Hard limits
- Never diagnose or replace professional mental health support.
- If a user shows signs of crisis (self-harm, hopelessness), acknowledge with care and
  gently suggest talking to a counsellor or trusted person.

## Conversation examples (learn from these patterns)
{build_few_shot_block()}
"""

SYSTEM_PROMPT = _build_system_prompt()


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
    # Initialise TTS synchronously on the main thread before Flask starts.
    # This is important for macOS (nsss driver) and Windows (SAPI5) alike.
    init_tts()

    # Start the dedicated TTS worker thread (serialises all pyttsx3 calls).
    if TTS_ENABLED:
        t = threading.Thread(target=_tts_worker, daemon=True)
        t.start()

    # use_reloader=False: prevents Flask from spawning a child process,
    # which would create a second pyttsx3 engine and cause conflicts.
    app.run(debug=True, port=5000, use_reloader=False)
