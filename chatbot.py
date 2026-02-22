# chat-bot.py

import logging
import os

# Enable debug mode
DEBUG_MODE = True

# Configure logging for error logging
logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('app.log'),
                        logging.StreamHandler()
                    ])

# Example function demonstrating error logging

def some_function():
    try:
        # Your code logic here
        pass
    except Exception as e:
        logging.error(f'Error occurred: {e}')

# Rest of your chatbot code goes here...