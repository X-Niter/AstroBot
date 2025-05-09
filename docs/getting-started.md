# Getting Started with AstroBot

This guide will help you get started with AstroBot, from installation to basic usage.

## Requirements

Before installing AstroBot, make sure you have:

- Python 3.11 or higher
- Node.js 20 or higher
- PostgreSQL database
- Discord Bot Token (for bot functionality)
- Twitch API credentials (for Twitch integration)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/astrobot.git
   cd astrobot
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. Set up environment variables (see `.env.example`)

4. Initialize the database:

   ```bash
   python -m flask db upgrade
   ```

5. Start the application:

   ```bash
   python main.py
   ```

## Basic Usage

### Inviting the Bot to Your Discord Server

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to the "OAuth2" tab
4. In the "OAuth2 URL Generator", select the "bot" scope
5. Select the required permissions
6. Copy the generated URL and open it in your browser
7. Select the server to invite the bot to

### Basic Commands

- `!help` - Display help message
- `!status` - Check bot status
- `!config` - Configure bot settings

## Next Steps

Check out the [User Guide](user-guide.md) for more detailed information.