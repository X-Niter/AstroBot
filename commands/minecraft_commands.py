import discord
from discord import app_commands
from discord.ext import commands
import logging

from services.minecraft_service import (
    get_server_status, 
    whitelist_player, 
    remove_from_whitelist,
    execute_command,
    restart_server
)
from utils.embed_creator import create_minecraft_embed
from utils.permissions import is_admin, is_moderator
from utils.error_handler import handle_command_error

logger = logging.getLogger(__name__)

class MinecraftCommands(commands.Cog):
    """Commands for Minecraft server management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="server", description="Get Minecraft server status")
    async def server_status(self, interaction: discord.Interaction):
        """Get the current status of the Minecraft server"""
        await interaction.response.defer(thinking=True)
        
        try:
            status = await get_server_status()
            
            embed = create_minecraft_embed(
                title="Minecraft Server Status",
                description="Current server information and stats"
            )
            
            if status["online"]:
                embed.add_field(name="Status", value="🟢 Online", inline=True)
                embed.add_field(name="Players", value=f"{status['players_online']}/{status['max_players']}", inline=True)
                embed.add_field(name="Version", value=status["version"], inline=True)
                
                # Add player list if there are online players
                if status["players_online"] > 0 and status["player_list"]:
                    embed.add_field(
                        name="Online Players",
                        value="\n".join(status["player_list"]),
                        inline=False
                    )
            else:
                embed.add_field(name="Status", value="🔴 Offline", inline=True)
                embed.description = "The server appears to be offline or unreachable."
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /server command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="whitelist", description="Add a player to the server whitelist")
    @app_commands.describe(
        username="Minecraft username to add to the whitelist"
    )
    async def whitelist_add(self, interaction: discord.Interaction, username: str):
        """Add a player to the server whitelist"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Check if user has permission
            if not await is_moderator(interaction.user):
                await interaction.followup.send(
                    "You don't have permission to use this command. Only moderators can manage the whitelist.",
                    ephemeral=True
                )
                return
            
            result = await whitelist_player(username)
            
            if result["success"]:
                embed = create_minecraft_embed(
                    title="Whitelist Updated",
                    description=f"Successfully added **{username}** to the server whitelist."
                )
                await interaction.followup.send(embed=embed)
            else:
                embed = create_minecraft_embed(
                    title="Whitelist Error",
                    description=f"Failed to add player to whitelist: {result['message']}",
                    is_error=True
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /whitelist command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="whitelist_remove", description="Remove a player from the server whitelist")
    @app_commands.describe(
        username="Minecraft username to remove from the whitelist"
    )
    async def whitelist_remove(self, interaction: discord.Interaction, username: str):
        """Remove a player from the server whitelist"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Check if user has permission
            if not await is_moderator(interaction.user):
                await interaction.followup.send(
                    "You don't have permission to use this command. Only moderators can manage the whitelist.",
                    ephemeral=True
                )
                return
            
            result = await remove_from_whitelist(username)
            
            if result["success"]:
                embed = create_minecraft_embed(
                    title="Whitelist Updated",
                    description=f"Successfully removed **{username}** from the server whitelist."
                )
                await interaction.followup.send(embed=embed)
            else:
                embed = create_minecraft_embed(
                    title="Whitelist Error",
                    description=f"Failed to remove player from whitelist: {result['message']}",
                    is_error=True
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /whitelist_remove command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="execute", description="Execute a command on the Minecraft server")
    @app_commands.describe(
        command="The command to execute (without the leading /)"
    )
    async def execute(self, interaction: discord.Interaction, command: str):
        """Execute a command on the Minecraft server"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Check if user has permission
            if not await is_admin(interaction.user):
                await interaction.followup.send(
                    "You don't have permission to use this command. Only administrators can execute server commands.",
                    ephemeral=True
                )
                return
            
            result = await execute_command(command)
            
            if result["success"]:
                embed = create_minecraft_embed(
                    title="Command Executed",
                    description=f"Successfully executed command on the server."
                )
                
                # Add response if present
                if result["response"]:
                    embed.add_field(
                        name="Server Response",
                        value=f"```\n{result['response']}\n```",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                embed = create_minecraft_embed(
                    title="Command Error",
                    description=f"Failed to execute command: {result['message']}",
                    is_error=True
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /execute command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="restart", description="Restart the Minecraft server")
    async def restart(self, interaction: discord.Interaction):
        """Restart the Minecraft server"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Check if user has permission
            if not await is_admin(interaction.user):
                await interaction.followup.send(
                    "You don't have permission to use this command. Only administrators can restart the server.",
                    ephemeral=True
                )
                return
            
            result = await restart_server()
            
            if result["success"]:
                embed = create_minecraft_embed(
                    title="Server Restart",
                    description="The Minecraft server is being restarted. This may take a few minutes."
                )
                await interaction.followup.send(embed=embed)
            else:
                embed = create_minecraft_embed(
                    title="Restart Error",
                    description=f"Failed to restart server: {result['message']}",
                    is_error=True
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /restart command: {str(e)}")
            await handle_command_error(interaction, e)
