"""
Utility functions for creating rich embedded messages with consistent styling.
"""
import datetime
import discord
from typing import Optional, List, Dict, Any


def create_moderation_embed(
    title: str,
    description: str = None,
    user: str = None,
    user_id: str = None,
    moderator: str = None,
    reason: str = None,
    dm_sent: bool = None,
    color: int = 0x3273DC,  # Default AstroBot blue
    include_timestamp: bool = False
) -> discord.Embed:
    """
    Create a standardized embed for moderation actions
    
    Args:
        title: Title of the embed
        description: Description text
        user: Username of the affected user
        user_id: Discord ID of the affected user
        moderator: Username of the moderator
        reason: Reason for the action
        dm_sent: Whether a DM was sent to the user
        color: Color of the embed (hex integer)
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    # Add user information if provided
    if user:
        embed.add_field(name="User", value=user, inline=True)
        
    if user_id:
        embed.add_field(name="User ID", value=user_id, inline=True)
    
    # Add moderator information if provided
    if moderator:
        embed.add_field(name="Moderator", value=moderator, inline=True)
    
    # Add reason if provided
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    
    # Add DM status if provided
    if dm_sent is not None:
        dm_status = "✅ DM Sent" if dm_sent else "❌ Could not DM user"
        embed.add_field(name="Notification", value=dm_status, inline=True)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    return embed


def create_custom_command_embed(
    title: str,
    description: str = None,
    fields: list = None,
    color: int = 0x3273DC,  # Default AstroBot blue
    include_timestamp: bool = False,
    footer_text: str = None,
    author_name: str = None,
    author_icon_url: str = None,
    thumbnail_url: str = None,
    image_url: str = None
) -> discord.Embed:
    """
    Create a standardized embed for custom commands
    
    Args:
        title: Title of the embed
        description: Description text
        fields: List of field dictionaries with {name, value, inline} keys
        color: Color of the embed (hex integer)
        include_timestamp: Whether to include a timestamp
        footer_text: Text to display in the footer
        author_name: Name to display in the author field
        author_icon_url: URL for the author icon
        thumbnail_url: URL for the thumbnail image
        image_url: URL for the main image
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    # Add fields if provided
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", True)
            )
    
    # Add author if provided
    if author_name:
        embed.set_author(
            name=author_name,
            icon_url=author_icon_url
        )
    
    # Add thumbnail if provided
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Add image if provided
    if image_url:
        embed.set_image(url=image_url)
    
    # Add footer if provided
    if footer_text:
        embed.set_footer(text=footer_text)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    return embed


def create_analytics_embed(
    title: str,
    description: str = None,
    data_points: dict = None,
    chart_url: str = None,
    color: int = 0x3273DC,  # Default AstroBot blue
    include_timestamp: bool = False
) -> discord.Embed:
    """
    Create a standardized embed for analytics data
    
    Args:
        title: Title of the embed
        description: Description text
        data_points: Dictionary of data points to display as fields
        chart_url: URL to a chart image 
        color: Color of the embed (hex integer)
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    # Add data points as fields
    if data_points:
        for name, value in data_points.items():
            embed.add_field(name=name, value=value, inline=True)
    
    # Add chart if provided
    if chart_url:
        embed.set_image(url=chart_url)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
        
    # Add AstroBot analytics footer
    embed.set_footer(text="AstroBot Analytics")
    
    return embed


def create_minecraft_embed(
    title: str,
    description: str = None,
    server_name: str = None,
    server_status: str = None,
    player_count: str = None,
    version: str = None,
    address: str = None,
    color: int = 0x5CB85C,  # Green
    thumbnail_url: Optional[str] = None,
    include_timestamp: bool = True
) -> discord.Embed:
    """
    Create a standardized embed for Minecraft server information
    
    Args:
        title: Title of the embed
        description: Description text
        server_name: Name of the Minecraft server
        server_status: Status of the server (online/offline)
        player_count: Player count information
        version: Minecraft version
        address: Server address
        color: Color of the embed
        thumbnail_url: URL for the thumbnail image
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    # Add server information if provided
    if server_name:
        embed.add_field(name="Server", value=server_name, inline=True)
        
    if server_status:
        # Set color based on status
        if server_status.lower() == "online":
            embed.color = 0x5CB85C  # Green
        elif server_status.lower() == "offline":
            embed.color = 0xD9534F  # Red
        embed.add_field(name="Status", value=server_status, inline=True)
    
    if player_count:
        embed.add_field(name="Players", value=player_count, inline=True)
        
    if version:
        embed.add_field(name="Version", value=version, inline=True)
        
    if address:
        embed.add_field(name="Address", value=f"`{address}`", inline=True)
    
    # Add thumbnail if provided
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    # Add footer
    embed.set_footer(text="AstroBot Minecraft")
    
    return embed


def create_ai_response_embed(
    title: str,
    response: str,
    query: str = None,
    model: str = None,
    color: int = 0x9B59B6,  # Purple
    thumbnail_url: Optional[str] = None,
    include_timestamp: bool = True
) -> discord.Embed:
    """
    Create a standardized embed for AI responses
    
    Args:
        title: Title of the embed
        response: The AI-generated response
        query: User's original query
        model: Name of the AI model used
        color: Color of the embed
        thumbnail_url: URL for the thumbnail image
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        description=response,
        color=color
    )
    
    # Add query if provided
    if query:
        embed.add_field(name="Query", value=query, inline=False)
    
    # Add model information if provided
    if model:
        embed.add_field(name="AI Model", value=model, inline=True)
    
    # Add thumbnail if provided
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    # Add footer
    embed.set_footer(text="AstroBot AI")
    
    return embed


def create_twitch_embed(
    title: str,
    streamer: str = None,
    stream_title: str = None,
    game: str = None,
    viewer_count: int = None,
    stream_url: str = None,
    thumbnail_url: Optional[str] = None,
    color: int = 0x6441A4,  # Twitch purple
    include_timestamp: bool = True
) -> discord.Embed:
    """
    Create a standardized embed for Twitch streams
    
    Args:
        title: Title of the embed
        streamer: Name of the Twitch streamer
        stream_title: Title of the stream
        game: Game being played
        viewer_count: Number of viewers
        stream_url: URL to the Twitch stream
        thumbnail_url: URL for the thumbnail image
        color: Color of the embed
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        url=stream_url,
        color=color
    )
    
    # Add streamer information if provided
    if streamer:
        embed.add_field(name="Streamer", value=streamer, inline=True)
        
    if stream_title:
        embed.add_field(name="Stream Title", value=stream_title, inline=False)
    
    if game:
        embed.add_field(name="Game", value=game, inline=True)
        
    if viewer_count is not None:
        embed.add_field(name="Viewers", value=f"{viewer_count:,}", inline=True)
        
    if stream_url:
        embed.add_field(name="Watch", value=f"[Twitch]({stream_url})", inline=True)
    
    # Add thumbnail if provided
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    # Add footer
    embed.set_footer(text="AstroBot Twitch Integration")
    
    return embed


def create_leaderboard_embed(
    title: str,
    leaderboard_entries: List[Dict[str, Any]],
    description: str = None,
    field_name: str = "Top Users",
    rank_icon: str = "🏆",
    color: int = 0xF1C40F,  # Gold
    thumbnail_url: Optional[str] = None,
    include_timestamp: bool = True
) -> discord.Embed:
    """
    Create a standardized embed for leaderboards
    
    Args:
        title: Title of the embed
        leaderboard_entries: List of dictionaries with leaderboard data
        description: Description text
        field_name: Name of the leaderboard field
        rank_icon: Icon to use for ranking
        color: Color of the embed
        thumbnail_url: URL for the thumbnail image
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    # Format leaderboard entries
    if leaderboard_entries:
        leaderboard_text = ""
        
        for i, entry in enumerate(leaderboard_entries):
            rank = i + 1
            rank_prefix = f"{rank}. "
            
            # Add special icons for top 3
            if rank == 1:
                rank_prefix = "🥇 "
            elif rank == 2:
                rank_prefix = "🥈 "
            elif rank == 3:
                rank_prefix = "🥉 "
                
            # Format entry based on available fields
            if "name" in entry and "score" in entry:
                leaderboard_text += f"{rank_prefix}**{entry['name']}** - {entry['score']:,} points\n"
            elif "name" in entry and "value" in entry:
                leaderboard_text += f"{rank_prefix}**{entry['name']}** - {entry['value']}\n"
            elif "user" in entry and "score" in entry:
                leaderboard_text += f"{rank_prefix}**{entry['user']}** - {entry['score']:,} points\n"
            else:
                # Generic fallback
                leaderboard_text += f"{rank_prefix}{str(entry)}\n"
                
        embed.add_field(name=field_name, value=leaderboard_text, inline=False)
    else:
        embed.add_field(name=field_name, value="No entries found", inline=False)
    
    # Add thumbnail if provided
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    # Add footer
    embed.set_footer(text="AstroBot Leaderboard")
    
    return embed


def create_mod_embed(
    title: str,
    description: str = None,
    mod_action: str = None,
    target_user: str = None,
    reason: str = None,
    duration: str = None,
    color: int = 0xFF3860,  # Red
    thumbnail_url: Optional[str] = None,
    include_timestamp: bool = True
) -> discord.Embed:
    """
    Create a standardized embed for community moderation actions
    
    Args:
        title: Title of the embed
        description: Description text
        mod_action: Type of moderation action (ban, mute, etc.)
        target_user: User who received the moderation action
        reason: Reason for the moderation action
        duration: Duration of the moderation action
        color: Color of the embed
        thumbnail_url: URL for the thumbnail image
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    # Add action information if provided
    if mod_action:
        embed.add_field(name="Action", value=mod_action, inline=True)
        
    if target_user:
        embed.add_field(name="User", value=target_user, inline=True)
    
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
        
    if duration:
        embed.add_field(name="Duration", value=duration, inline=True)
    
    # Add thumbnail if provided
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    # Add footer
    embed.set_footer(text="AstroBot Community Moderation")
    
    return embed


def create_feedback_embed(
    user: str,
    feedback: str,
    feedback_type: str = "Suggestion",
    contact_info: str = None,
    feedback_id: str = None,
    status: str = "Submitted",
    color: int = 0x3498DB,  # Blue
    include_timestamp: bool = True
) -> discord.Embed:
    """
    Create a standardized embed for user feedback/suggestions
    
    Args:
        user: Name of the user providing feedback
        feedback: The feedback content
        feedback_type: Type of feedback (Suggestion, Bug Report, etc.)
        contact_info: Optional contact information
        feedback_id: Optional feedback ID for tracking
        status: Status of the feedback
        color: Color of the embed
        include_timestamp: Whether to include a timestamp
        
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(
        title=f"{feedback_type} #{feedback_id}" if feedback_id else feedback_type,
        description=feedback,
        color=color
    )
    
    # Add user information
    embed.add_field(name="From", value=user, inline=True)
    
    # Add status
    embed.add_field(name="Status", value=status, inline=True)
    
    # Add contact info if provided
    if contact_info:
        embed.add_field(name="Contact Info", value=contact_info, inline=True)
    
    # Add timestamp if requested
    if include_timestamp:
        embed.timestamp = datetime.datetime.utcnow()
    
    # Add footer
    embed.set_footer(text="AstroBot Feedback System")
    
    return embed


def create_welcome_embed(
    guild_name: str,
    member_name: str,
    description: str = None,
    rules_text: str = None,
    color: int = 0x00D26A,  # Green
    member_count: Optional[int] = None,
    thumbnail_url: Optional[str] = None,
    image_url: Optional[str] = None
) -> discord.Embed:
    """
    Create a standardized welcome embed
    
    Args:
        guild_name: Name of the Discord server
        member_name: Name of the new member
        description: Custom welcome message
        rules_text: Server rules to display
        color: Color of the embed
        member_count: Current member count of the server
        thumbnail_url: URL for the thumbnail (e.g., server icon)
        image_url: URL for the main image (e.g., welcome banner)
        
    Returns:
        discord.Embed: The created embed
    """
    # Default description if none provided
    if description is None:
        description = f"Welcome to **{guild_name}**, {member_name}! We're glad to have you here!"
    
    embed = discord.Embed(
        title=f"Welcome to {guild_name}!",
        description=description,
        color=color
    )
    
    # Add member count if provided
    if member_count is not None:
        embed.add_field(name="Member Count", value=f"You are the {member_count}th member!", inline=False)
    
    # Add rules if provided
    if rules_text:
        embed.add_field(name="Server Rules", value=rules_text, inline=False)
    
    # Add thumbnail if provided
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    # Add image if provided
    if image_url:
        embed.set_image(url=image_url)
    
    # Add timestamp
    embed.timestamp = datetime.datetime.utcnow()
    
    # Add footer
    embed.set_footer(text=f"Join Date: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return embed