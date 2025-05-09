import os

# Discord Bot Configuration
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
COMMAND_PREFIX = "!"

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_MODEL = "gpt-4o"

# Anthropic Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
# the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
# do not change this unless explicitly requested by the user
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# Twitch Configuration
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")

# MongoDB Configuration
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/astrobot")
DB_NAME = os.environ.get("DB_NAME", "astrobot")
MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.environ.get("MONGODB_PORT", 27017))
MONGODB_USERNAME = os.environ.get("MONGODB_USERNAME", "")
MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD", "")
# If direct connection URI is not provided, build one from components
if not MONGODB_URI or MONGODB_URI == "mongodb://localhost:27017/astrobot":
    # Build connection string based on credentials
    if MONGODB_USERNAME and MONGODB_PASSWORD:
        MONGODB_URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{DB_NAME}"
    else:
        MONGODB_URI = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/{DB_NAME}"

# Minecraft Server Configuration
MINECRAFT_SERVER_IP = os.environ.get("MINECRAFT_SERVER_IP", "localhost")
MINECRAFT_SERVER_PORT = int(os.environ.get("MINECRAFT_SERVER_PORT", "25575"))
MINECRAFT_RCON_PASSWORD = os.environ.get("MINECRAFT_RCON_PASSWORD", "")

# Role configuration for points system
POINTS_ROLES = {
    "Novice": 100,
    "Apprentice": 500,
    "Explorer": 1000,
    "Expert": 5000,
    "Master": 10000,
    "Legend": 25000
}

# Bot theme colors (RGB hex values)
COLORS = {
    "PRIMARY": 0x007bff,  # Neon blue
    "SUCCESS": 0x00d26a,  # Neon green
    "ERROR": 0xff3860,    # Red
    "WARNING": 0xffdd57,  # Yellow
    "INFO": 0x3273dc,     # Blue
    "MINECRAFT": 0x4fce6a, # Minecraft green
    "TWITCH": 0x9146ff,   # Twitch purple
    "AI": 0x00d0ff        # AI blue
}
