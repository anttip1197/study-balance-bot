# Study Balance Bot

## Installation Instructions

### Requirements
- Python 3.6+
- Pip (Python package installer)

### Set Up Virtual Environment
1. Navigate to the project directory:
   ```bash
   cd path/to/study-balance-bot
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

### Install Dependencies
Run the following command to install the required packages:
```bash
pip install -r requirements.txt
```

### Set Up ElevenLabs API
1. Obtain your API key from [ElevenLabs](https://elevenlabs.io/).
2. Set your API key as an environment variable:
   ```bash
   export ELEVENLABS_API_KEY='your_api_key'  # macOS/Linux
   set ELEVENLABS_API_KEY='your_api_key'     # Windows
   ```

### Running the Bot
To run the bot, execute the following command:
```bash
python chatbot.py
```

You can access it at [http://127.0.0.1:5000](http://127.0.0.1:5000).