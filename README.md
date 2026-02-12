# Study Balance Bot

## Requirements
- Python 3.8 or higher

## Installation

## Install Git Bash
1. Download the Git Bash installer from https://gitforwindows.org/
2. Run the installer and follow the installation instructions.
3. Once installed, you can use Git Bash to run the scripts and commands needed for the Study Balance Bot.

## Clone Repo to yout PC

   git clone https://github.com/anttip1197/study-balance-bot.git

   Change to the directory:

   cd study-balance-bot

### Setting Up API Keys

You will need to set up two API keys for the bot to function properly:

1. **ElevenLabs API Key**:
   - Sign up at [ElevenLabs](https://www.elevenlabs.io).
   - Retrieve your API key from the dashboard and store it securely.

2. **Google API Key**:
   - Go to the Google Cloud Console at [console.cloud.google.com](https://console.cloud.google.com).
   - Create a new project and enable the required APIs.
   - Generate your API key from the credentials page.

### Configuration

Edit the `.env` file in the root directory of the project with the following content:

```env
ELEVEN_LABS_API_KEY=your_eleven_labs_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

Replace `your_eleven_labs_api_key_here` and `your_google_api_key_here` with your actual API keys.

### Running the Bot

## 2. Install Dependencies:

    pip install flask flask-cors elevenlabs python-dotenv google-genai

## 3. Configure Environment:

    Create a .env file in the root directory:
    
    Plaintext
    ELEVENLABS_API_KEY=your_key_here
    GEMINI_API_KEY=your_key_here

## 4. Launch Application:
    
    python chatbot.py
    
    The server will run on http://127.0.0.1:5000.
    
##  Project Structure
    - chatbot.py: Flask backend managing AI logic and API orchestrations.
    - index.html: Clean, responsive frontend chat interface.
    - static/: Local cache for generated audio .mp3 files.
    - .env: Secure storage for sensitive API credentials.
   
## 👥 Project Team
    
    Antti Parviainen
    Eveliina Knuutila
    Madina Khasaeva
    Sirke Sahranto
"@
