from elevenlabs import save
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Generoi audio
audio = client.text_to_speech.convert(
    voice_id="21m00Tcm4TlvDq8ikWAM",
    text="Hei, tämä on testi ElevenLabs API:lla!",
    model_id="eleven_multilingual_v2"
)

# Tallenna
save(audio, "output.mp3")
print("Valmis! Tarkista output.mp3")