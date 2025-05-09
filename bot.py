import os
import discord
from discord.ext import commands
import logging

# Import command cogs
from commands.ai_commands import AICommands
from commands.minecraft_commands import MinecraftCommands
from commands.twitch_commands import TwitchCommands
from commands.community_commands import CommunityCommands
from utils.error_handler import setup_error_handlers

logger = logging.getLogger(__name__)

def setup_bot():
    """Set up the Discord bot with all necessary configurations and commands."""
    # Set up intents
    intents = discord.Intents.default()
    intents.message_content = True  # For access to message content
    intents.members = True  # For access to member information

    # Create the bot with a command prefix and intents
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Event: Bot is ready
    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
        logger.info(f"Connected to {len(bot.guilds)} guilds")
        
        # Set bot presence
        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name="/help | AstroBot"
        )
        await bot.change_presence(activity=activity)
        
        # Sync slash commands
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    # Add command cogs
    @bot.event
    async def setup_hook():
        # Add cogs to the bot
        await bot.add_cog(AICommands(bot))
        await bot.add_cog(MinecraftCommands(bot))
        await bot.add_cog(TwitchCommands(bot))
        await bot.add_cog(CommunityCommands(bot))
        
        # Setup error handlers
        setup_error_handlers(bot)

    return bot
