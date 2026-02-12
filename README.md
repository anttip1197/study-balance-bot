# Study Balance Bot

## Requirements
- Python 3.8 or higher

## Installation

### Install Git Bash
1. Download the Git Bash installer from https://gitforwindows.org/
2. Run the installer and follow the installation instructions.
3. Once installed, you can use Git Bash to run the scripts and commands needed for the Study Balance Bot.

# Additional Information

   git clone https://github.com/anttip1197/study-balance-bot.git
   ```

3. Change to the directory:

   ```bash
   cd study-balance-bot
   ```

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

Create a `.env` file in the root directory of the project with the following content:

```env
ELEVEN_LABS_API_KEY=your_eleven_labs_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

Replace `your_eleven_labs_api_key_here` and `your_google_api_key_here` with your actual API keys.

### Running the Bot

To run the bot, follow these commands:

1. Install the required packages:

   ```bash
   npm install
   ```

2. Start the bot:

   ```bash
   npm start
   ```

You should see the bot running in your terminal. 

### Support

For any issues or feature requests, please open an issue in the GitHub repository.
