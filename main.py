import os
import logging
import threading
from bot import setup_bot
from app import app  # Import for gunicorn to work

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Function to run the Discord bot in a separate thread
def run_bot():
    # Setup and run the bot
    bot = setup_bot()
    
    # Get Discord token from environment variables
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logging.error("DISCORD_TOKEN environment variable not set")
        return
    
    # Run the bot
    bot.run(token)

if __name__ == "__main__":
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
