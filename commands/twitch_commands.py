import discord
from discord import app_commands
from discord.ext import commands
import logging

from services.twitch_service import (
    get_stream_info,
    get_user_info,
    get_clips,
    award_points
)
from services.mongo_service import (
    get_user_points,
    get_leaderboard,
    link_twitch_account
)
from utils.embed_creator import create_twitch_embed, create_leaderboard_embed
from utils.permissions import is_moderator
from utils.error_handler import handle_command_error

logger = logging.getLogger(__name__)

class TwitchCommands(commands.Cog):
    """Commands for Twitch integration and StreamSync features"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="stream", description="Get info about a Twitch stream")
    @app_commands.describe(
        username="Twitch username to check"
    )
    async def stream(self, interaction: discord.Interaction, username: str):
        """Get information about a Twitch stream"""
        await interaction.response.defer(thinking=True)
        
        try:
            stream_info = await get_stream_info(username)
            
            if stream_info["is_live"]:
                embed = create_twitch_embed(
                    title=f"{username} is Live on Twitch!",
                    description=stream_info["title"],
                    url=f"https://twitch.tv/{username}"
                )
                
                embed.add_field(name="Game", value=stream_info["game"], inline=True)
                embed.add_field(name="Viewers", value=str(stream_info["viewers"]), inline=True)
                embed.add_field(name="Started", value=stream_info["started_at"], inline=True)
                
                if stream_info["thumbnail_url"]:
                    # Replace width and height parameters in the thumbnail URL
                    thumbnail = stream_info["thumbnail_url"].replace("{width}", "440").replace("{height}", "248")
                    embed.set_image(url=thumbnail)
                
                await interaction.followup.send(embed=embed)
            else:
                embed = create_twitch_embed(
                    title=f"{username} is Offline",
                    description="This channel is not currently streaming.",
                    url=f"https://twitch.tv/{username}"
                )
                
                # If we have the user's profile picture, add it
                if stream_info["profile_image_url"]:
                    embed.set_thumbnail(url=stream_info["profile_image_url"])
                
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /stream command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="clips", description="Get recent clips from a Twitch channel")
    @app_commands.describe(
        username="Twitch username to get clips from",
        limit="Number of clips to fetch (default: 3, max: 5)"
    )
    async def clips(self, interaction: discord.Interaction, username: str, limit: int = 3):
        """Get recent clips from a Twitch channel"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Limit the number of clips
            if limit > 5:
                limit = 5
            
            clips = await get_clips(username, limit)
            
            if clips and len(clips) > 0:
                embed = create_twitch_embed(
                    title=f"Recent Clips from {username}",
                    description=f"Here are the {len(clips)} most recent clips from this channel:",
                    url=f"https://twitch.tv/{username}/clips"
                )
                
                for i, clip in enumerate(clips):
                    embed.add_field(
                        name=f"{i+1}. {clip['title']}",
                        value=f"[Watch Clip]({clip['url']}) - {clip['view_count']} views",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                embed = create_twitch_embed(
                    title=f"No Clips Found",
                    description=f"Could not find any recent clips for {username}.",
                    url=f"https://twitch.tv/{username}"
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /clips command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="points", description="Check your support points")
    async def points(self, interaction: discord.Interaction):
        """Check your support points"""
        await interaction.response.defer(thinking=True)
        
        try:
            user_points = await get_user_points(str(interaction.user.id))
            
            embed = create_twitch_embed(
                title="Support Points",
                description=f"{interaction.user.display_name}'s community contribution stats"
            )
            
            embed.add_field(name="Total Points", value=str(user_points["points"]), inline=True)
            embed.add_field(name="Current Rank", value=user_points["rank"], inline=True)
            
            # Show progress to next rank if available
            if user_points["next_rank"]:
                points_needed = user_points["next_rank_points"] - user_points["points"]
                embed.add_field(
                    name="Next Rank",
                    value=f"{user_points['next_rank']} ({points_needed} points needed)",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /points command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="leaderboard", description="View the community support leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """View the community support leaderboard"""
        await interaction.response.defer(thinking=True)
        
        try:
            leaderboard_data = await get_leaderboard()
            
            embed = create_leaderboard_embed(
                title="Community Support Leaderboard",
                description="Top community contributors based on support points",
                leaderboard_data=leaderboard_data,
                guild=interaction.guild
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /leaderboard command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="link", description="Link your Twitch account")
    @app_commands.describe(
        twitch_username="Your Twitch username to link"
    )
    async def link(self, interaction: discord.Interaction, twitch_username: str):
        """Link your Discord account to your Twitch account"""
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        try:
            # Get Twitch user info to verify the account exists
            twitch_user = await get_user_info(twitch_username)
            
            if not twitch_user:
                await interaction.followup.send(
                    f"Could not find Twitch user '{twitch_username}'. Please check the spelling and try again.",
                    ephemeral=True
                )
                return
            
            # Link the accounts
            result = await link_twitch_account(
                discord_id=str(interaction.user.id),
                twitch_id=twitch_user["id"],
                twitch_username=twitch_username
            )
            
            if result["success"]:
                embed = create_twitch_embed(
                    title="Account Linked",
                    description=f"Successfully linked your Discord account to Twitch user **{twitch_username}**."
                )
                embed.set_thumbnail(url=twitch_user["profile_image_url"])
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    f"Failed to link accounts: {result['message']}",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"Error in /link command: {str(e)}")
            await handle_command_error(interaction, e, ephemeral=True)
    
    @app_commands.command(name="award", description="Award support points to a user")
    @app_commands.describe(
        user="User to award points to",
        points="Number of points to award",
        reason="Reason for awarding points"
    )
    async def award(
        self, 
        interaction: discord.Interaction, 
        user: discord.User, 
        points: int, 
        reason: str
    ):
        """Award support points to a user"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Check if user has permission
            if not await is_moderator(interaction.user):
                await interaction.followup.send(
                    "You don't have permission to use this command. Only moderators can award points.",
                    ephemeral=True
                )
                return
            
            # Validate points amount
            if points <= 0:
                await interaction.followup.send(
                    "Points must be a positive number.",
                    ephemeral=True
                )
                return
            
            result = await award_points(
                discord_id=str(user.id),
                points=points,
                reason=reason,
                awarded_by=str(interaction.user.id)
            )
            
            if result["success"]:
                embed = create_twitch_embed(
                    title="Points Awarded",
                    description=f"Successfully awarded **{points}** support points to {user.mention}!"
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="New Total", value=str(result["new_total"]), inline=True)
                embed.add_field(name="Rank", value=result["rank"], inline=True)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    f"Failed to award points: {result['message']}",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"Error in /award command: {str(e)}")
            await handle_command_error(interaction, e)
