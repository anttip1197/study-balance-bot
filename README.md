$readmeContent = @"
# Study-Work Balance Support Chatbot
**Course Project: HTI-560-2026**

A supportive and empathetic conversational chatbot designed for students balancing the pressures of work and academia. This project leverages the **Gemini 2.0 Flash** model for high-speed, intelligent emotional validation and **ElevenLabs** for warm, human-like voice synthesis.

## 🌟 Key Features
- 💬 **Empathetic Dialogue**: Focuses on emotional validation rather than direct prescriptive advice.
- 🔊 **Voice Integration**: Automatic text-to-speech using the ElevenLabs 'Rachel' voice.
- 🧠 **Smart Context**: Maintains a session-based conversation history for more meaningful interactions.
- ⚡ **Optimized Responses**: Prompt engineered to keep replies warm and concise (2-4 sentences) to avoid sentence cut-offs.

## ⚙️ Prerequisites
- **Python 3.9+**
- **ElevenLabs API Key**
- **Google Gemini API Key** (Obtain from [Google AI Studio](https://aistudio.google.com/))

## 🛠️ Installation & Setup
1. **Clone & Navigate**:
   ```bash
    cd elevenlabs
   
## 2. Install Dependencies:

    pip install flask flask-cors elevenlabs python-dotenv google-genai

## 3. Configure Environment:

    Create a .env file in the root directory:
    
    Plaintext
    ELEVENLABS_API_KEY=your_key_here
    GEMINI_API_KEY=your_key_here

## 4. Launch Application:
    
    Bash
    python chatbot.py
    The server will run on http://127.0.0.1:5000.
    
    📂 Project Structure
    chatbot.py: Flask backend managing AI logic and API orchestrations.
    
    index.html: Clean, responsive frontend chat interface.
    
    static/: Local cache for generated audio .mp3 files.
    
    .env: Secure storage for sensitive API credentials.
    
    🤝 Design Principles
    Based on research for the HTI-560 course, the bot adheres to:
    
    Self-Reflection: Encouraging users to explore their own workload feelings.
    
    Non-Judgmental Tone: Creating a safe space for students to vent.
    
    Brevity: Limiting output tokens to ensure clear, complete voice delivery.
    
    👥 Project Team
    Antti Parviainen
    
    Eveliina Knuutila
    
    Madina Khasaeva
    
    Sirke Sahranto
"@