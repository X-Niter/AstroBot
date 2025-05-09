import discord
from datetime import datetime

from config import COLORS

def create_ai_response_embed(title, description, model_name, query=None):
    """
    Create an embed for AI responses
    
    Args:
        title (str): The embed title
        description (str): The response content
        model_name (str): Name of the AI model used
        query (str, optional): The original query
        
    Returns:
        discord.Embed: The formatted embed
    """
    embed = discord.Embed(
        title=title,
        description=description if len(description) <= 4000 else description[:3997] + "...",
        color=COLORS["AI"],
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text=f"Powered by {model_name}")
    
    if query:
        embed.add_field(name="Query", value=query if len(query) <= 1024 else query[:1021] + "...", inline=False)
    
    return embed

def create_minecraft_embed(title, description, is_error=False):
    """
    Create an embed for Minecraft server commands
    
    Args:
        title (str): The embed title
        description (str): The embed description
        is_error (bool): Whether this is an error message
        
    Returns:
        discord.Embed: The formatted embed
    """
    color = COLORS["ERROR"] if is_error else COLORS["MINECRAFT"]
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="Minecraft Server Management")
    
    return embed

def create_twitch_embed(title, description, url=None):
    """
    Create an embed for Twitch-related commands
    
    Args:
        title (str): The embed title
        description (str): The embed description
        url (str, optional): URL to link in the title
        
    Returns:
        discord.Embed: The formatted embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLORS["TWITCH"],
        timestamp=datetime.utcnow(),
        url=url
    )
    
    embed.set_footer(text="StreamSync Integration")
    
    return embed

def create_leaderboard_embed(title, description, leaderboard_data, guild):
    """
    Create an embed for the support points leaderboard
    
    Args:
        title (str): The embed title
        description (str): The embed description
        leaderboard_data (list): List of users with points data
        guild (discord.Guild): The Discord guild
        
    Returns:
        discord.Embed: The formatted embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLORS["PRIMARY"],
        timestamp=datetime.utcnow()
    )
    
    # Add leaderboard entries
    for i, entry in enumerate(leaderboard_data):
        # Try to get the user's display name
        user = guild.get_member(int(entry["discord_id"]))
        display_name = user.display_name if user else f"User {entry['discord_id']}"
        
        # Add medal emoji for top 3
        prefix = ""
        if i == 0:
            prefix = "🥇 "
        elif i == 1:
            prefix = "🥈 "
        elif i == 2:
            prefix = "🥉 "
        else:
            prefix = f"{i+1}. "
        
        embed.add_field(
            name=f"{prefix}{display_name}",
            value=f"**{entry['points']}** points • {entry['rank']}",
            inline=(i >= 3)  # Top 3 not inline, others are inline
        )
    
    embed.set_footer(text="StreamSync Leaderboard")
    
    return embed

def create_mod_embed(title, description):
    """
    Create an embed for mod-related commands
    
    Args:
        title (str): The embed title
        description (str): The embed description
        
    Returns:
        discord.Embed: The formatted embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLORS["INFO"],
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="Minecraft Mod Community")
    
    return embed
