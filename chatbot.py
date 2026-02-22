from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
import requests
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

SYSTEM_INSTRUCTION = (
    "You are a supportive and empathetic assistant helping students who are "
    "struggling with balancing work and studies. Your role is to: listen actively "
    "and validate their feelings, provide practical advice on time management and "
    "stress reduction, offer encouragement and emotional support, suggest healthy "
    "coping strategies, and help them prioritize and plan their workload. "
    "Be warm, understanding, and constructive in your responses."
)

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

conversation_sessions = {}


def get_elevenlabs_response(message, history):
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json',
    }
    payload = {
        'system_prompt': SYSTEM_INSTRUCTION,
        'conversation_history': history,
        'message': message,
    }
    response = requests.post(
        'https://api.elevenlabs.io/v1/convai/conversation',
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data.get('response') or data.get('text', '')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = []

    history = conversation_sessions[session_id]

    try:
        bot_response = get_elevenlabs_response(user_message, history)

        conversation_sessions[session_id].append({'role': 'user', 'content': user_message})
        conversation_sessions[session_id].append({'role': 'assistant', 'content': bot_response})

        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)

        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=bot_response,
            model_id="eleven_monolingual_v1",
        )
        with open(audio_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)

        return jsonify({'response': bot_response, 'audio_url': f"/audio/{audio_filename}"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/audio/<filename>')
def serve_audio(filename):
    if '/' in filename or '\\' in filename or filename.startswith('.'):
        return jsonify({'error': 'Invalid filename'}), 400
    return send_from_directory(AUDIO_DIR, filename)


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')