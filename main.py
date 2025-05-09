import os
import logging
from bot import setup_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Setup and run the bot
    bot = setup_bot()
    
    # Get Discord token from environment variables
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logging.error("DISCORD_TOKEN environment variable not set")
        exit(1)
    
    # Run the bot
    bot.run(token)
