from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os
from google import genai  # Use the new unified SDK
from google.genai import types

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Clients
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# The new Client automatically looks for GEMINI_API_KEY in your .env
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# System instruction for the bot
SYSTEM_INSTRUCTION = """You are a supportive and empathetic chatbot for students. 
Focus on emotional validation and self-reflection. Use a warm, natural tone.

CRITICAL CONSTRAINTS:
- Keep every response between 2 and 4 sentences.
- Never exceed 80 words total.
- Ensure your response is complete and does not end abruptly.
- Prioritize being brief while remaining warm."""

# Store conversation history
conversations = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')

    # Simple history management for this example
    if session_id not in conversations:
        conversations[session_id] = []

    # Add user message to local history
    conversations[session_id].append(
        {"role": "user", "parts": [{"text": user_message}]})

    try:
        # Use 'gemini-2.0-flash' for the latest free features
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=conversations[session_id],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=400,
            ),
        )

        bot_response = response.text

        # Add bot response to local history
        conversations[session_id].append(
            {"role": "model", "parts": [{"text": bot_response}]})

        # Generate audio with ElevenLabs
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            text=bot_response,
            model_id="eleven_multilingual_v2"
        )

        audio_filename = f"audio_{session_id}_{len(conversations[session_id])}.mp3"
        audio_path = os.path.join('static', audio_filename)
        os.makedirs('static', exist_ok=True)

        with open(audio_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)

        return jsonify({
            'response': bot_response,
            'audio_url': f'/static/{audio_filename}'
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)