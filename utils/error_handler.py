import discord
import logging
import traceback
from discord.ext import commands

from config import COLORS

logger = logging.getLogger(__name__)

async def handle_command_error(interaction, error, ephemeral=False):
    """
    Handle errors from slash commands
    
    Args:
        interaction (discord.Interaction): The interaction that caused the error
        error (Exception): The error that occurred
        ephemeral (bool): Whether to send the error message as ephemeral (only visible to the user)
    """
    error_message = str(error)
    
    # Log the full error with traceback
    logger.error(f"Command error: {error}")
    logger.error(traceback.format_exc())
    
    # Create an error embed
    embed = discord.Embed(
        title="Error",
        description=f"An error occurred while processing your command:\n```\n{error_message}\n```",
        color=COLORS["ERROR"]
    )
    
    # Send the error message
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=ephemeral)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

def setup_error_handlers(bot):
    """
    Set up global error handlers for the bot
    
    Args:
        bot (commands.Bot): The discord.py bot instance
    """
    @bot.event
    async def on_command_error(ctx, error):
        """Handle errors from prefix commands"""
        # Ignore command not found errors
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Create an error embed
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while processing your command:\n```\n{str(error)}\n```",
            color=COLORS["ERROR"]
        )
        
        await ctx.send(embed=embed)
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        """Handle general errors"""
        logger.error(f"An error occurred in event {event}")
        logger.error(traceback.format_exc())
