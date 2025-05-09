# Command descriptions
COMMAND_DESCRIPTIONS = {
    "ask": "Ask the AI assistant a question",
    "fix": "Fix code or troubleshoot Minecraft mod issues",
    "idea": "Generate a Minecraft mod idea",
    "tutorial": "Generate a Minecraft modding tutorial",
    "server": "Get Minecraft server status",
    "whitelist": "Add a player to the server whitelist",
    "whitelist_remove": "Remove a player from the server whitelist",
    "execute": "Execute a command on the Minecraft server",
    "restart": "Restart the Minecraft server",
    "stream": "Get info about a Twitch stream",
    "clips": "Get recent clips from a Twitch channel",
    "points": "Check your support points",
    "leaderboard": "View the community support leaderboard",
    "link": "Link your Twitch account",
    "award": "Award support points to a user",
    "review": "Submit a review for a Minecraft mod",
    "find": "Find reviews for a Minecraft mod",
    "suggest": "Suggest a new Minecraft mod idea",
    "browse": "Browse recent mod suggestions"
}

# AI models
AI_MODELS = {
    "gpt": {
        "name": "GPT-4o",
        "description": "OpenAI's latest multimodal model"
    },
    "claude": {
        "name": "Claude 3.5",
        "description": "Anthropic's advanced AI assistant"
    }
}

# Help categories
HELP_CATEGORIES = {
    "ai": {
        "name": "AI Assistance",
        "description": "Commands for AI-powered help with Minecraft modding",
        "commands": ["ask", "fix", "idea", "tutorial"]
    },
    "minecraft": {
        "name": "Minecraft Server",
        "description": "Commands for managing the Minecraft server",
        "commands": ["server", "whitelist", "whitelist_remove", "execute", "restart"]
    },
    "twitch": {
        "name": "Twitch Integration",
        "description": "Commands for StreamSync and Twitch features",
        "commands": ["stream", "clips", "points", "leaderboard", "link", "award"]
    },
    "community": {
        "name": "Community Tools",
        "description": "Commands for mod reviews and suggestions",
        "commands": ["review", "find", "suggest", "browse"]
    }
}

# Example prompts for AI commands
EXAMPLE_PROMPTS = {
    "ask": [
        "How do I create a custom entity in Minecraft Forge?",
        "What are the differences between Forge and Fabric?",
        "How do I fix 'java.lang.NullPointerException' in my mod?"
    ],
    "fix": [
        "My entity isn't spawning in the world",
        "Getting 'NoSuchMethodError' when launching my mod",
        "Items disappear when I place them in my custom inventory"
    ],
    "idea": [
        "A mod that adds underwater biomes and creatures",
        "A tech mod focused on renewable energy",
        "A magic mod with spell crafting"
    ],
    "tutorial": [
        "Creating custom blocks in Forge",
        "Setting up a development environment for modding",
        "Implementing custom world generation"
    ]
}
