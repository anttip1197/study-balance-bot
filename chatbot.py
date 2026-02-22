import openai
import requests

class ElevenLabsConvAI:
    def __init__(self, api_key):
        self.api_key = api_key

    def chat(self, prompt):
        response = requests.post(
            'https://api.elevenlabs.io/v1/conversation',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={'prompt': prompt}
        )
        response_data = response.json()
        return response_data['response']

    def text_to_speech(self, text):
        response = requests.post(
            'https://api.elevenlabs.io/v1/text-to-speech',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={'text': text}
        )
        audio_url = response.json()['audio_url']
        return audio_url

# Example Usage
if __name__ == '__main__':
    api_key = 'YOUR_ELEVENLABS_API_KEY'
    chatbot = ElevenLabsConvAI(api_key)
    user_input = 'Hello, how can I help you today?'
    response = chatbot.chat(user_input)
    print('Bot:', response)
    audio_url = chatbot.text_to_speech(response)
    print('Audio URL:', audio_url)