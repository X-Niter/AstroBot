"""
AstroBot AI Enhanced Custom Commands System
A powerful, AI-driven custom commands system that provides significant improvements over YAGPDB.
"""
import json
import logging
import re
import asyncio
import datetime
import traceback
from typing import Dict, List, Tuple, Optional, Any, Union, Set
from collections import defaultdict

import discord
from discord.ext import commands

from app import db
from models import (
    CustomCommand, CommandCategory, CommandVariable, 
    CommandUsage, CommandTemplate, CommandGroup
)
from services.ai_service import generate_command_suggestion
from utils.embed_creator import create_custom_command_embed

logger = logging.getLogger(__name__)

class AdvancedCustomCommandsSystem:
    """
    Enhanced custom commands system with visual command builder, templates,
    variable storage, and AI-powered suggestions.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.commands_cache = {}  # guild_id: {trigger: command_obj}
        self.groups_cache = {}  # guild_id: {group_id: group_obj}
        self.variables_cache = {}  # guild_id: {var_name: var_obj}
        self.cooldowns = defaultdict(dict)  # {guild_id: {cmd_id: {user_id: timestamp}}}
        self.global_cooldowns = defaultdict(dict)  # {guild_id: {cmd_id: timestamp}}
        self.command_templates = []  # List of available templates
        self.api_integrations = {
            "weather": self._api_weather,
            "jokes": self._api_jokes,
            "randomfact": self._api_random_fact,
            "translate": self._api_translate,
            "define": self._api_define,
            "crypto": self._api_crypto,
            "wiki": self._api_wiki
        }
        
    async def initialize(self):
        """Initialize the custom commands system on bot startup"""
        # Load all custom commands into cache
        await self.load_commands()
        # Load command groups
        await self.load_command_groups()
        # Load command variables
        await self.load_command_variables()
        # Load command templates
        await self.load_command_templates()
        # Register listeners
        self.bot.add_listener(self.on_message, "on_message")
        logger.info("Advanced Custom Commands System initialized")
        
    async def load_commands(self):
        """Load all custom commands into cache"""
        try:
            # Query database for all custom commands
            commands = db.session.query(CustomCommand).filter_by(enabled=True).all()
            
            # Organize commands by guild
            for cmd in commands:
                guild_id = cmd.guild_id
                if guild_id not in self.commands_cache:
                    self.commands_cache[guild_id] = {}
                    
                self.commands_cache[guild_id][cmd.trigger.lower()] = cmd
                
            logger.info(f"Loaded {len(commands)} custom commands")
        except Exception as e:
            logger.error(f"Error loading custom commands: {str(e)}")
            
    async def load_command_groups(self):
        """Load command groups"""
        try:
            # Query database for all command groups
            groups = db.session.query(CommandGroup).all()
            
            # Organize groups by guild
            for group in groups:
                guild_id = group.guild_id
                if guild_id not in self.groups_cache:
                    self.groups_cache[guild_id] = {}
                    
                self.groups_cache[guild_id][group.id] = group
                
            logger.info(f"Loaded {len(groups)} command groups")
        except Exception as e:
            logger.error(f"Error loading command groups: {str(e)}")
            
    async def load_command_variables(self):
        """Load command variables"""
        try:
            # Query database for all command variables
            variables = db.session.query(CommandVariable).all()
            
            # Organize variables by guild
            for var in variables:
                guild_id = var.guild_id
                if guild_id not in self.variables_cache:
                    self.variables_cache[guild_id] = {}
                    
                self.variables_cache[guild_id][var.name] = var
                
            logger.info(f"Loaded {len(variables)} command variables")
        except Exception as e:
            logger.error(f"Error loading command variables: {str(e)}")
            
    async def load_command_templates(self):
        """Load command templates"""
        try:
            # Query database for all command templates
            templates = db.session.query(CommandTemplate).all()
            
            # Store templates in list
            self.command_templates = templates
                
            logger.info(f"Loaded {len(templates)} command templates")
        except Exception as e:
            logger.error(f"Error loading command templates: {str(e)}")
            
    async def reload_guild_commands(self, guild_id: str):
        """
        Reload commands for a specific guild
        
        Args:
            guild_id: Discord ID of the guild
        """
        try:
            # Remove current guild commands from cache
            if guild_id in self.commands_cache:
                del self.commands_cache[guild_id]
                
            # Query database for guild's custom commands
            commands = db.session.query(CustomCommand).filter_by(
                guild_id=guild_id,
                enabled=True
            ).all()
            
            # Add to cache
            self.commands_cache[guild_id] = {}
            for cmd in commands:
                self.commands_cache[guild_id][cmd.trigger.lower()] = cmd
                
            logger.info(f"Reloaded {len(commands)} commands for guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error reloading commands for guild {guild_id}: {str(e)}")
            return False
            
    async def reload_guild_variables(self, guild_id: str):
        """
        Reload variables for a specific guild
        
        Args:
            guild_id: Discord ID of the guild
        """
        try:
            # Remove current guild variables from cache
            if guild_id in self.variables_cache:
                del self.variables_cache[guild_id]
                
            # Query database for guild's variables
            variables = db.session.query(CommandVariable).filter_by(guild_id=guild_id).all()
            
            # Add to cache
            self.variables_cache[guild_id] = {}
            for var in variables:
                self.variables_cache[guild_id][var.name] = var
                
            logger.info(f"Reloaded {len(variables)} variables for guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error reloading variables for guild {guild_id}: {str(e)}")
            return False
            
    async def reload_guild_groups(self, guild_id: str):
        """
        Reload command groups for a specific guild
        
        Args:
            guild_id: Discord ID of the guild
        """
        try:
            # Remove current guild groups from cache
            if guild_id in self.groups_cache:
                del self.groups_cache[guild_id]
                
            # Query database for guild's command groups
            groups = db.session.query(CommandGroup).filter_by(guild_id=guild_id).all()
            
            # Add to cache
            self.groups_cache[guild_id] = {}
            for group in groups:
                self.groups_cache[guild_id][group.id] = group
                
            logger.info(f"Reloaded {len(groups)} groups for guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error reloading groups for guild {guild_id}: {str(e)}")
            return False
    
    async def on_message(self, message: discord.Message):
        """Handle message events for custom command execution"""
        # Ignore messages from bots
        if message.author.bot:
            return
            
        # Ignore DMs
        if not message.guild:
            return
            
        # Check for commands
        await self.check_and_execute_commands(message)
    
    async def check_and_execute_commands(self, message: discord.Message):
        """
        Check if message triggers any custom commands and execute if so
        
        Args:
            message: The Discord message
        """
        guild_id = str(message.guild.id)
        
        # Guild has no custom commands
        if guild_id not in self.commands_cache:
            return
            
        content = message.content.strip()
        
        # Check for commands with exact match
        exact_triggers = {}
        for trigger, cmd in self.commands_cache[guild_id].items():
            if cmd.trigger_type == "exact" and content.lower() == trigger.lower():
                exact_triggers[trigger] = cmd
                
        # Check for startswith triggers if no exact match
        startswith_triggers = {}
        if not exact_triggers:
            for trigger, cmd in self.commands_cache[guild_id].items():
                if cmd.trigger_type == "startswith" and content.lower().startswith(trigger.lower() + " "):
                    startswith_triggers[trigger] = cmd
                    
        # Check for contains triggers if no exact or startswith match
        contains_triggers = {}
        if not exact_triggers and not startswith_triggers:
            for trigger, cmd in self.commands_cache[guild_id].items():
                if cmd.trigger_type == "contains" and trigger.lower() in content.lower():
                    contains_triggers[trigger] = cmd
                    
        # Check for regex triggers if no other matches
        regex_triggers = {}
        if not exact_triggers and not startswith_triggers and not contains_triggers:
            for trigger, cmd in self.commands_cache[guild_id].items():
                if cmd.trigger_type == "regex":
                    try:
                        pattern = re.compile(trigger, re.IGNORECASE)
                        if pattern.search(content):
                            regex_triggers[trigger] = cmd
                    except Exception as e:
                        logger.error(f"Invalid regex pattern for command {cmd.id}: {str(e)}")
        
        # Get all triggered commands
        triggered_commands = {}
        triggered_commands.update(exact_triggers)
        triggered_commands.update(startswith_triggers)
        triggered_commands.update(contains_triggers)
        triggered_commands.update(regex_triggers)
        
        # Sort by trigger length (longest first) and then by priority
        sorted_triggers = sorted(
            triggered_commands.keys(),
            key=lambda t: (-len(t), -triggered_commands[t].priority)
        )
        
        # Execute commands until a terminate flag is found
        for trigger in sorted_triggers:
            cmd = triggered_commands[trigger]
            
            # Check if command passes conditions
            if not await self.check_command_conditions(cmd, message):
                continue
                
            # Execute the command
            executed = await self.execute_custom_command(cmd, message)
            
            # Stop processing if command terminated
            if executed and cmd.terminate_processing:
                break
    
    async def check_command_conditions(self, cmd: CustomCommand, message: discord.Message) -> bool:
        """
        Check if a command's conditions are met for execution
        
        Args:
            cmd: The custom command
            message: The Discord message
            
        Returns:
            bool: Whether conditions are met
        """
        try:
            # Get command settings
            settings = json.loads(cmd.settings) if cmd.settings else {}
            
            # Check channel restrictions
            if settings.get("channel_whitelist"):
                channels = [str(c.strip()) for c in settings["channel_whitelist"].split(",")]
                if str(message.channel.id) not in channels:
                    return False
                    
            if settings.get("channel_blacklist"):
                channels = [str(c.strip()) for c in settings["channel_blacklist"].split(",")]
                if str(message.channel.id) in channels:
                    return False
            
            # Check role restrictions
            if settings.get("role_whitelist"):
                roles = [str(r.strip()) for r in settings["role_whitelist"].split(",")]
                member_roles = [str(r.id) for r in message.author.roles]
                if not any(r in member_roles for r in roles):
                    return False
                    
            if settings.get("role_blacklist"):
                roles = [str(r.strip()) for r in settings["role_blacklist"].split(",")]
                member_roles = [str(r.id) for r in message.author.roles]
                if any(r in member_roles for r in roles):
                    return False
            
            # Check command group
            if cmd.group_id and settings.get("enforce_group_restrictions", True):
                if not await self.check_group_permissions(cmd.group_id, message.author):
                    return False
            
            # Check cooldowns
            if not await self.check_command_cooldowns(cmd, message):
                return False
            
            # Check custom conditions
            if settings.get("custom_condition"):
                condition = settings["custom_condition"]
                condition_met = await self.evaluate_custom_condition(condition, message)
                if not condition_met:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking command conditions: {str(e)}")
            return False
    
    async def check_group_permissions(self, group_id: int, member: discord.Member) -> bool:
        """
        Check if a member has permission to use commands from a group
        
        Args:
            group_id: The ID of the command group
            member: The Discord member
            
        Returns:
            bool: Whether the member has permission
        """
        try:
            guild_id = str(member.guild.id)
            
            # Get group from cache
            if guild_id not in self.groups_cache or group_id not in self.groups_cache[guild_id]:
                return False
                
            group = self.groups_cache[guild_id][group_id]
            
            # Check role requirements
            if group.required_roles:
                roles = [str(r.strip()) for r in group.required_roles.split(",")]
                member_roles = [str(r.id) for r in member.roles]
                if not any(r in member_roles for r in roles):
                    return False
                    
            # Check permission requirements
            if group.required_permissions:
                permissions = [p.strip() for p in group.required_permissions.split(",")]
                member_permissions = [p[0] for p in member.guild_permissions if p[1]]
                if not all(p in member_permissions for p in permissions):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking group permissions: {str(e)}")
            return False
    
    async def check_command_cooldowns(self, cmd: CustomCommand, message: discord.Message) -> bool:
        """
        Check if a command is on cooldown for the user
        
        Args:
            cmd: The custom command
            message: The Discord message
            
        Returns:
            bool: Whether the command is not on cooldown
        """
        try:
            # Get command settings
            settings = json.loads(cmd.settings) if cmd.settings else {}
            
            # Get cooldown settings
            user_cooldown = settings.get("user_cooldown", 0)
            global_cooldown = settings.get("global_cooldown", 0)
            
            # No cooldowns set
            if not user_cooldown and not global_cooldown:
                return True
                
            now = datetime.datetime.utcnow().timestamp()
            guild_id = str(message.guild.id)
            cmd_id = cmd.id
            user_id = str(message.author.id)
            
            # Check user cooldown
            if user_cooldown > 0:
                if guild_id in self.cooldowns and cmd_id in self.cooldowns[guild_id]:
                    if user_id in self.cooldowns[guild_id][cmd_id]:
                        last_used = self.cooldowns[guild_id][cmd_id][user_id]
                        if now - last_used < user_cooldown:
                            # Still on cooldown
                            remaining = int(user_cooldown - (now - last_used))
                            
                            # Check if user should be notified
                            if settings.get("notify_cooldown", True):
                                if remaining > 60:
                                    minutes = remaining // 60
                                    seconds = remaining % 60
                                    cooldown_msg = f"This command is on cooldown for {minutes}m {seconds}s"
                                else:
                                    cooldown_msg = f"This command is on cooldown for {remaining}s"
                                    
                                await message.channel.send(cooldown_msg, delete_after=5)
                                
                            return False
            
            # Check global cooldown
            if global_cooldown > 0:
                if guild_id in self.global_cooldowns and cmd_id in self.global_cooldowns[guild_id]:
                    last_used = self.global_cooldowns[guild_id][cmd_id]
                    if now - last_used < global_cooldown:
                        # Still on global cooldown
                        if settings.get("notify_cooldown", True):
                            remaining = int(global_cooldown - (now - last_used))
                            if remaining > 60:
                                minutes = remaining // 60
                                seconds = remaining % 60
                                cooldown_msg = f"This command is on global cooldown for {minutes}m {seconds}s"
                            else:
                                cooldown_msg = f"This command is on global cooldown for {remaining}s"
                                
                            await message.channel.send(cooldown_msg, delete_after=5)
                        
                        return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking command cooldowns: {str(e)}")
            return True  # On error, allow command to run
    
    async def evaluate_custom_condition(self, condition: str, message: discord.Message) -> bool:
        """
        Evaluate a custom condition for a command
        
        Args:
            condition: The condition to evaluate
            message: The Discord message
            
        Returns:
            bool: Whether the condition is met
        """
        try:
            # Create a safe context with limited variables
            ctx = {
                "message": message,
                "user_id": str(message.author.id),
                "channel_id": str(message.channel.id),
                "guild_id": str(message.guild.id),
                "day_of_week": datetime.datetime.utcnow().strftime("%A").lower(),
                "hour": datetime.datetime.utcnow().hour,
                "minute": datetime.datetime.utcnow().minute,
                "re": re,
                "random": __import__("random")
            }
            
            # Add variables from cache
            guild_id = str(message.guild.id)
            if guild_id in self.variables_cache:
                for var_name, var_obj in self.variables_cache[guild_id].items():
                    ctx[f"var_{var_name}"] = var_obj.value
            
            # Sanitize the condition (remove dangerous functions)
            if re.search(r"(__[\w]+__|exec|eval|compile|open|file|\bimport\b)", condition):
                logger.warning(f"Dangerous function detected in condition: {condition}")
                return False
                
            # Evaluate the condition
            result = eval(condition, {"__builtins__": {}}, ctx)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error evaluating custom condition: {str(e)}")
            return False
    
    async def execute_custom_command(self, cmd: CustomCommand, message: discord.Message) -> bool:
        """
        Execute a custom command
        
        Args:
            cmd: The custom command to execute
            message: The Discord message that triggered it
            
        Returns:
            bool: Whether the command executed successfully
        """
        try:
            # Update cooldowns
            self.update_command_cooldowns(cmd, message)
            
            # Parse command content
            response_content = await self.parse_command_content(cmd, message)
            
            # Check for empty response
            if not response_content:
                logger.warning(f"Command {cmd.id} produced empty response")
                return False
                
            # Get command settings
            settings = json.loads(cmd.settings) if cmd.settings else {}
            
            # Check for dynamic response type
            if "{{" in response_content and "}}" in response_content:
                # Extract the response type
                match = re.match(r"^{{([a-z_]+)}}\s*(.*)$", response_content, re.DOTALL)
                if match:
                    response_type = match.group(1)
                    response_content = match.group(2)
                    
                    # Override the stored response type
                    settings["response_type"] = response_type
            
            # Get response type
            response_type = settings.get("response_type", "text")
            
            # Handle different response types
            if response_type == "text":
                await message.channel.send(response_content)
                
            elif response_type == "embed":
                try:
                    # Parse embed JSON
                    embed_data = json.loads(response_content)
                    embed = await self.create_embed_from_data(embed_data)
                    await message.channel.send(embed=embed)
                except Exception as embed_error:
                    logger.error(f"Error parsing embed: {str(embed_error)}")
                    await message.channel.send(f"Error parsing embed: {str(embed_error)}")
                    
            elif response_type == "reaction":
                # Add reactions to the message
                for emoji in response_content.split():
                    try:
                        await message.add_reaction(emoji.strip())
                    except Exception as e:
                        logger.error(f"Error adding reaction {emoji}: {str(e)}")
                        
            elif response_type == "dm":
                try:
                    await message.author.send(response_content)
                    # Add a checkmark reaction if DM was sent
                    await message.add_reaction("✅")
                except Exception as e:
                    logger.error(f"Error sending DM: {str(e)}")
                    await message.add_reaction("❌")
                    
            elif response_type == "file":
                # Generate a file from the response content
                file_buffer = discord.File(
                    filename=settings.get("filename", "file.txt"),
                    fp=response_content.encode("utf-8")
                )
                await message.channel.send(file=file_buffer)
                
            elif response_type == "complex":
                try:
                    # Parse complex response JSON
                    complex_data = json.loads(response_content)
                    
                    # Extract components
                    content = complex_data.get("content", "")
                    embed_data = complex_data.get("embed")
                    
                    # Create embed if specified
                    embed = await self.create_embed_from_data(embed_data) if embed_data else None
                    
                    # Send the message
                    await message.channel.send(content=content, embed=embed)
                    
                except Exception as complex_error:
                    logger.error(f"Error parsing complex response: {str(complex_error)}")
                    await message.channel.send(f"Error parsing complex response: {str(complex_error)}")
            
            # Record command usage
            self.record_command_usage(cmd, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing custom command: {str(e)}\n{traceback.format_exc()}")
            # Send error message if configured
            try:
                settings = json.loads(cmd.settings) if cmd.settings else {}
                if settings.get("show_errors", True):
                    await message.channel.send(f"Error executing command: {str(e)}")
            except:
                pass
                
            return False
    
    def update_command_cooldowns(self, cmd: CustomCommand, message: discord.Message):
        """
        Update cooldown timestamps for a command
        
        Args:
            cmd: The custom command
            message: The Discord message that triggered it
        """
        try:
            # Get command settings
            settings = json.loads(cmd.settings) if cmd.settings else {}
            
            # Get cooldown settings
            user_cooldown = settings.get("user_cooldown", 0)
            global_cooldown = settings.get("global_cooldown", 0)
            
            # No cooldowns set
            if not user_cooldown and not global_cooldown:
                return
                
            now = datetime.datetime.utcnow().timestamp()
            guild_id = str(message.guild.id)
            cmd_id = cmd.id
            user_id = str(message.author.id)
            
            # Update user cooldown
            if user_cooldown > 0:
                if guild_id not in self.cooldowns:
                    self.cooldowns[guild_id] = {}
                if cmd_id not in self.cooldowns[guild_id]:
                    self.cooldowns[guild_id][cmd_id] = {}
                    
                self.cooldowns[guild_id][cmd_id][user_id] = now
            
            # Update global cooldown
            if global_cooldown > 0:
                if guild_id not in self.global_cooldowns:
                    self.global_cooldowns[guild_id] = {}
                    
                self.global_cooldowns[guild_id][cmd_id] = now
                
        except Exception as e:
            logger.error(f"Error updating command cooldowns: {str(e)}")
    
    async def parse_command_content(self, cmd: CustomCommand, message: discord.Message) -> str:
        """
        Parse command content, replacing variables and executing any dynamic code
        
        Args:
            cmd: The custom command
            message: The Discord message that triggered it
            
        Returns:
            str: The parsed command content
        """
        try:
            content = cmd.response_content
            
            # Handle empty content
            if not content:
                return "Error: Command has no content"
                
            # Replace built-in variables
            content = await self.replace_built_in_variables(content, message)
            
            # Replace custom variables
            content = await self.replace_custom_variables(content, message)
            
            # Handle API integrations
            content = await self.handle_api_integrations(content, message)
            
            # Handle logic blocks (if/else)
            content = await self.handle_logic_blocks(content, message)
            
            # Handle loops
            content = await self.handle_loops(content, message)
            
            # Handle random selection blocks
            content = await self.handle_random_blocks(content, message)
            
            return content
            
        except Exception as e:
            logger.error(f"Error parsing command content: {str(e)}")
            return f"Error parsing command: {str(e)}"
    
    async def replace_built_in_variables(self, content: str, message: discord.Message) -> str:
        """
        Replace built-in variables in command content
        
        Args:
            content: The command content
            message: The Discord message
            
        Returns:
            str: Content with variables replaced
        """
        try:
            # User variables
            content = content.replace("{{user}}", str(message.author))
            content = content.replace("{{user.mention}}", message.author.mention)
            content = content.replace("{{user.id}}", str(message.author.id))
            content = content.replace("{{user.name}}", message.author.name)
            content = content.replace("{{user.nick}}", message.author.nick or message.author.name)
            content = content.replace("{{user.avatar}}", str(message.author.avatar_url))
            
            # Server variables
            content = content.replace("{{server}}", message.guild.name)
            content = content.replace("{{server.id}}", str(message.guild.id))
            content = content.replace("{{server.icon}}", str(message.guild.icon_url))
            content = content.replace("{{server.membercount}}", str(message.guild.member_count))
            
            # Channel variables
            content = content.replace("{{channel}}", message.channel.name)
            content = content.replace("{{channel.mention}}", message.channel.mention)
            content = content.replace("{{channel.id}}", str(message.channel.id))
            
            # Message variables
            content = content.replace("{{message.id}}", str(message.id))
            content = content.replace("{{message.content}}", message.content)
            
            # Time variables
            now = datetime.datetime.utcnow()
            content = content.replace("{{time}}", now.strftime("%H:%M:%S"))
            content = content.replace("{{date}}", now.strftime("%Y-%m-%d"))
            content = content.replace("{{datetime}}", now.strftime("%Y-%m-%d %H:%M:%S"))
            content = content.replace("{{timestamp}}", str(int(now.timestamp())))
            
            # Other variables
            content = content.replace("{{newline}}", "\n")
            content = content.replace("{{nl}}", "\n")
            
            # Handle arguments
            args = message.content.split()[1:] if " " in message.content else []
            content = content.replace("{{args}}", " ".join(args))
            
            # Replace {{argN}} with the Nth argument
            arg_matches = re.findall(r"{{arg(\d+)}}", content)
            for match in arg_matches:
                index = int(match)
                if index < len(args):
                    content = content.replace(f"{{arg{index}}}", args[index])
                else:
                    content = content.replace(f"{{arg{index}}}", "")
            
            return content
            
        except Exception as e:
            logger.error(f"Error replacing built-in variables: {str(e)}")
            return content
    
    async def replace_custom_variables(self, content: str, message: discord.Message) -> str:
        """
        Replace custom variables and handle variable assignments
        
        Args:
            content: The command content
            message: The Discord message
            
        Returns:
            str: Content with variables replaced
        """
        try:
            guild_id = str(message.guild.id)
            
            # Handle variable assignments {{setvar name value}}
            setvar_pattern = r"{{setvar\s+([a-zA-Z0-9_]+)\s+(.+?)}}"
            setvar_matches = re.findall(setvar_pattern, content)
            
            for match in setvar_matches:
                var_name = match[0]
                var_value = match[1]
                
                # Replace any nested variables in the value
                var_value = await self.replace_built_in_variables(var_value, message)
                
                # Save or update the variable
                await self.set_command_variable(guild_id, var_name, var_value)
                
                # Remove the setvar statement from the content
                content = content.replace(f"{{setvar {var_name} {var_value}}}", "")
            
            # Replace variable references {{var name}}
            var_pattern = r"{{var\s+([a-zA-Z0-9_]+)}}"
            var_matches = re.findall(var_pattern, content)
            
            for var_name in var_matches:
                var_value = await self.get_command_variable(guild_id, var_name)
                content = content.replace(f"{{var {var_name}}}", var_value or "")
                
            # Handle increment {{incr name}}
            incr_pattern = r"{{incr\s+([a-zA-Z0-9_]+)}}"
            incr_matches = re.findall(incr_pattern, content)
            
            for var_name in incr_matches:
                var_value = await self.get_command_variable(guild_id, var_name)
                
                try:
                    # Convert to int and increment
                    if var_value and var_value.isdigit():
                        new_value = str(int(var_value) + 1)
                    else:
                        new_value = "1"
                        
                    # Save the new value
                    await self.set_command_variable(guild_id, var_name, new_value)
                    
                    # Replace the incr statement with the new value
                    content = content.replace(f"{{incr {var_name}}}", new_value)
                except Exception as e:
                    logger.error(f"Error incrementing variable {var_name}: {str(e)}")
                    content = content.replace(f"{{incr {var_name}}}", var_value or "0")
            
            return content
            
        except Exception as e:
            logger.error(f"Error replacing custom variables: {str(e)}")
            return content
    
    async def get_command_variable(self, guild_id: str, var_name: str) -> Optional[str]:
        """
        Get the value of a command variable
        
        Args:
            guild_id: The guild ID
            var_name: The variable name
            
        Returns:
            Optional[str]: The variable value, or None if not found
        """
        try:
            # Check if variable exists in cache
            if guild_id in self.variables_cache and var_name in self.variables_cache[guild_id]:
                return self.variables_cache[guild_id][var_name].value
                
            # Not in cache, query database
            var = db.session.query(CommandVariable).filter_by(
                guild_id=guild_id,
                name=var_name
            ).first()
            
            if var:
                # Add to cache
                if guild_id not in self.variables_cache:
                    self.variables_cache[guild_id] = {}
                    
                self.variables_cache[guild_id][var_name] = var
                return var.value
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting command variable: {str(e)}")
            return None
    
    async def set_command_variable(self, guild_id: str, var_name: str, var_value: str):
        """
        Set the value of a command variable
        
        Args:
            guild_id: The guild ID
            var_name: The variable name
            var_value: The variable value
        """
        try:
            # Check if variable exists
            var = db.session.query(CommandVariable).filter_by(
                guild_id=guild_id,
                name=var_name
            ).first()
            
            if var:
                # Update existing variable
                var.value = var_value
                var.updated_at = datetime.datetime.utcnow()
            else:
                # Create new variable
                var = CommandVariable(
                    guild_id=guild_id,
                    name=var_name,
                    value=var_value,
                    created_at=datetime.datetime.utcnow()
                )
                db.session.add(var)
                
            # Commit changes
            db.session.commit()
            
            # Update cache
            if guild_id not in self.variables_cache:
                self.variables_cache[guild_id] = {}
                
            self.variables_cache[guild_id][var_name] = var
            
        except Exception as e:
            logger.error(f"Error setting command variable: {str(e)}")
            db.session.rollback()
    
    async def handle_api_integrations(self, content: str, message: discord.Message) -> str:
        """
        Handle API integration blocks in command content
        
        Args:
            content: The command content
            message: The Discord message
            
        Returns:
            str: Content with API responses
        """
        try:
            # Look for API blocks {{api_name args}}
            api_pattern = r"{{([a-z_]+)\s+(.+?)}}"
            
            # First pass to find all API calls
            api_calls = []
            for match in re.finditer(api_pattern, content):
                api_name = match.group(1)
                api_args = match.group(2)
                
                # Check if this is an API integration
                if api_name in self.api_integrations:
                    api_calls.append((match.group(0), api_name, api_args))
            
            # Process each API call
            for full_match, api_name, api_args in api_calls:
                api_func = self.api_integrations[api_name]
                
                # Call the API
                result = await api_func(api_args, message)
                
                # Replace the API call with the result
                content = content.replace(full_match, result)
            
            return content
            
        except Exception as e:
            logger.error(f"Error handling API integrations: {str(e)}")
            return content
    
    async def handle_logic_blocks(self, content: str, message: discord.Message) -> str:
        """
        Handle if/else logic blocks in command content
        
        Args:
            content: The command content
            message: The Discord message
            
        Returns:
            str: Processed content with logic blocks evaluated
        """
        try:
            # Handle nested if blocks first
            while "{{if" in content and "{{endif}}" in content:
                # Find the innermost if block
                start_index = content.rfind("{{if", 0, content.find("{{endif}}"))
                if start_index == -1:
                    break
                    
                # Find the matching endif
                end_index = content.find("{{endif}}", start_index) + 9  # +9 for length of {{endif}}
                
                # Extract the if block
                if_block = content[start_index:end_index]
                
                # Parse the if statement
                match = re.match(r"{{if\s+(.+?)}}", if_block)
                if not match:
                    # Malformed if statement, remove it
                    content = content.replace(if_block, "")
                    continue
                    
                condition = match.group(1)
                
                # Check for else statement
                if "{{else}}" in if_block:
                    then_part = if_block[match.end():if_block.find("{{else}}")]
                    else_part = if_block[if_block.find("{{else}}") + 8:if_block.find("{{endif}}")]
                else:
                    then_part = if_block[match.end():if_block.find("{{endif}}")]
                    else_part = ""
                
                # Evaluate the condition
                condition_met = await self.evaluate_custom_condition(condition, message)
                
                # Replace the if block with the appropriate content
                if condition_met:
                    content = content.replace(if_block, then_part)
                else:
                    content = content.replace(if_block, else_part)
            
            return content
            
        except Exception as e:
            logger.error(f"Error handling logic blocks: {str(e)}")
            return content
    
    async def handle_loops(self, content: str, message: discord.Message) -> str:
        """
        Handle loop blocks in command content
        
        Args:
            content: The command content
            message: The Discord message
            
        Returns:
            str: Processed content with loops expanded
        """
        try:
            # Look for loop blocks {{loop N content}}
            loop_pattern = r"{{loop\s+(\d+)\s+(.+?){{endloop}}"
            
            # Find all loop blocks
            for match in re.finditer(loop_pattern, content, re.DOTALL):
                full_match = match.group(0) + "}}"  # Add the closing brackets
                count = int(match.group(1))
                loop_content = match.group(2)
                
                # Limit to prevent abuse
                if count > 20:
                    count = 20
                    
                # Expand the loop
                expanded = ""
                for i in range(count):
                    # Replace {{index}} with the current index
                    current = loop_content.replace("{{index}}", str(i))
                    expanded += current
                    
                # Replace the loop block with the expanded content
                content = content.replace(full_match, expanded)
            
            return content
            
        except Exception as e:
            logger.error(f"Error handling loops: {str(e)}")
            return content
    
    async def handle_random_blocks(self, content: str, message: discord.Message) -> str:
        """
        Handle random selection blocks in command content
        
        Args:
            content: The command content
            message: The Discord message
            
        Returns:
            str: Content with random selections made
        """
        try:
            import random
            
            # Look for random blocks {{random option1|option2|...}}
            random_pattern = r"{{random\s+(.+?)}}"
            
            # Find all random blocks
            for match in re.finditer(random_pattern, content):
                full_match = match.group(0)
                options_str = match.group(1)
                
                # Split options by pipe character
                options = options_str.split("|")
                
                # Select a random option
                if options:
                    selected = random.choice(options)
                else:
                    selected = ""
                    
                # Replace the random block with the selected option
                content = content.replace(full_match, selected)
            
            return content
            
        except Exception as e:
            logger.error(f"Error handling random blocks: {str(e)}")
            return content
    
    async def create_embed_from_data(self, data: Dict[str, Any]) -> discord.Embed:
        """
        Create a Discord embed from data
        
        Args:
            data: Embed data dictionary
            
        Returns:
            discord.Embed: The created embed
        """
        # Create base embed
        embed = discord.Embed()
        
        # Set basic properties
        if "title" in data:
            embed.title = data["title"]
            
        if "description" in data:
            embed.description = data["description"]
            
        if "url" in data:
            embed.url = data["url"]
            
        if "color" in data:
            # Handle color as int or hex string
            color = data["color"]
            if isinstance(color, str) and color.startswith("#"):
                color = int(color[1:], 16)
            embed.color = color
            
        if "timestamp" in data:
            if data["timestamp"] == "now":
                embed.timestamp = datetime.datetime.utcnow()
            else:
                try:
                    embed.timestamp = datetime.datetime.fromisoformat(data["timestamp"])
                except:
                    pass
        
        # Set author
        if "author" in data:
            name = data["author"].get("name", "")
            url = data["author"].get("url")
            icon_url = data["author"].get("icon_url")
            
            embed.set_author(name=name, url=url, icon_url=icon_url)
        
        # Set footer
        if "footer" in data:
            text = data["footer"].get("text", "")
            icon_url = data["footer"].get("icon_url")
            
            embed.set_footer(text=text, icon_url=icon_url)
        
        # Set thumbnail
        if "thumbnail" in data:
            embed.set_thumbnail(url=data["thumbnail"].get("url", ""))
        
        # Set image
        if "image" in data:
            embed.set_image(url=data["image"].get("url", ""))
        
        # Add fields
        if "fields" in data and isinstance(data["fields"], list):
            for field in data["fields"]:
                name = field.get("name", "")
                value = field.get("value", "")
                inline = field.get("inline", True)
                
                embed.add_field(name=name, value=value, inline=inline)
        
        return embed
    
    def record_command_usage(self, cmd: CustomCommand, message: discord.Message):
        """
        Record command usage for analytics
        
        Args:
            cmd: The custom command
            message: The Discord message
        """
        try:
            usage = CommandUsage(
                command_id=cmd.id,
                guild_id=str(message.guild.id),
                user_id=str(message.author.id),
                channel_id=str(message.channel.id),
                used_at=datetime.datetime.utcnow()
            )
            
            db.session.add(usage)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error recording command usage: {str(e)}")
            db.session.rollback()
    
    async def _api_weather(self, args: str, message: discord.Message) -> str:
        """Weather API integration"""
        # This would use a real weather API
        return f"Weather for {args}: 72°F, Sunny"
    
    async def _api_jokes(self, args: str, message: discord.Message) -> str:
        """Jokes API integration"""
        # This would use a real jokes API
        return "Why don't scientists trust atoms? Because they make up everything!"
    
    async def _api_random_fact(self, args: str, message: discord.Message) -> str:
        """Random fact API integration"""
        # This would use a real facts API
        return "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat."
    
    async def _api_translate(self, args: str, message: discord.Message) -> str:
        """Translation API integration"""
        # Format: {{translate from_lang to_lang text}}
        parts = args.split(maxsplit=2)
        if len(parts) != 3:
            return "Error: Invalid translation format"
            
        from_lang, to_lang, text = parts
        
        # This would use a real translation API
        return f"Translation ({from_lang} to {to_lang}): {text}"
    
    async def _api_define(self, args: str, message: discord.Message) -> str:
        """Dictionary API integration"""
        # This would use a real dictionary API
        return f"Definition of '{args}': a sample definition would appear here."
    
    async def _api_crypto(self, args: str, message: discord.Message) -> str:
        """Cryptocurrency price API integration"""
        # This would use a real crypto API
        return f"{args.upper()} price: $50,000"
    
    async def _api_wiki(self, args: str, message: discord.Message) -> str:
        """Wikipedia API integration"""
        # This would use a real Wikipedia API
        return f"Wikipedia summary for '{args}': This would be a brief summary from Wikipedia."

# Discord commands for custom commands management
class CustomCommandsCommands(commands.Cog):
    def __init__(self, bot, cmd_service):
        self.bot = bot
        self.cmd_service = cmd_service
    
    @commands.group(name="cc", invoke_without_command=True)
    @commands.guild_only()
    async def custom_commands(self, ctx):
        """Custom commands management"""
        await ctx.send("Please specify a subcommand. Use `!help cc` for more information")
    
    @custom_commands.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def add_command(self, ctx, trigger: str, *, response: str = None):
        """
        Add a simple custom command
        
        Args:
            ctx: The command context
            trigger: The trigger word for the command
            response: The response content
        """
        if not response:
            await ctx.send("You must provide a response for the command")
            return
            
        guild_id = str(ctx.guild.id)
        
        try:
            # Create new command
            new_cmd = CustomCommand(
                guild_id=guild_id,
                trigger=trigger,
                trigger_type="exact",
                response_content=response,
                created_by=str(ctx.author.id),
                created_at=datetime.datetime.utcnow(),
                enabled=True
            )
            
            db.session.add(new_cmd)
            db.session.commit()
            
            # Reload guild commands
            await self.cmd_service.reload_guild_commands(guild_id)
            
            # Respond to command
            await ctx.send(f"✅ Command `{trigger}` added successfully")
            
        except Exception as e:
            logger.error(f"Error adding custom command: {str(e)}")
            await ctx.send(f"Error adding command: {str(e)}")
            db.session.rollback()
    
    @custom_commands.command(name="edit")
    @commands.has_permissions(manage_guild=True)
    async def edit_command(self, ctx, trigger: str, *, response: str = None):
        """
        Edit an existing custom command
        
        Args:
            ctx: The command context
            trigger: The trigger word for the command
            response: The new response content
        """
        if not response:
            await ctx.send("You must provide a new response for the command")
            return
            
        guild_id = str(ctx.guild.id)
        
        try:
            # Find the command
            cmd = db.session.query(CustomCommand).filter_by(
                guild_id=guild_id,
                trigger=trigger
            ).first()
            
            if not cmd:
                await ctx.send(f"Command `{trigger}` not found")
                return
                
            # Update the command
            cmd.response_content = response
            cmd.updated_by = str(ctx.author.id)
            cmd.updated_at = datetime.datetime.utcnow()
            
            db.session.commit()
            
            # Reload guild commands
            await self.cmd_service.reload_guild_commands(guild_id)
            
            # Respond to command
            await ctx.send(f"✅ Command `{trigger}` updated successfully")
            
        except Exception as e:
            logger.error(f"Error editing custom command: {str(e)}")
            await ctx.send(f"Error editing command: {str(e)}")
            db.session.rollback()
    
    @custom_commands.command(name="delete", aliases=["remove"])
    @commands.has_permissions(manage_guild=True)
    async def delete_command(self, ctx, trigger: str):
        """
        Delete a custom command
        
        Args:
            ctx: The command context
            trigger: The trigger word for the command
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Find the command
            cmd = db.session.query(CustomCommand).filter_by(
                guild_id=guild_id,
                trigger=trigger
            ).first()
            
            if not cmd:
                await ctx.send(f"Command `{trigger}` not found")
                return
                
            # Delete the command
            db.session.delete(cmd)
            db.session.commit()
            
            # Reload guild commands
            await self.cmd_service.reload_guild_commands(guild_id)
            
            # Respond to command
            await ctx.send(f"✅ Command `{trigger}` deleted successfully")
            
        except Exception as e:
            logger.error(f"Error deleting custom command: {str(e)}")
            await ctx.send(f"Error deleting command: {str(e)}")
            db.session.rollback()
    
    @custom_commands.command(name="list")
    @commands.guild_only()
    async def list_commands(self, ctx):
        """List all custom commands in the server"""
        guild_id = str(ctx.guild.id)
        
        try:
            # Get all commands for the guild
            commands = db.session.query(CustomCommand).filter_by(guild_id=guild_id).all()
            
            if not commands:
                await ctx.send("No custom commands found")
                return
                
            # Organize commands by category
            by_category = {}
            for cmd in commands:
                category = "Default"
                if cmd.category_id:
                    category_obj = db.session.query(CommandCategory).filter_by(id=cmd.category_id).first()
                    if category_obj:
                        category = category_obj.name
                        
                if category not in by_category:
                    by_category[category] = []
                    
                by_category[category].append(cmd)
            
            # Create embed
            embed = discord.Embed(
                title="Custom Commands",
                description=f"This server has {len(commands)} custom commands",
                color=0x3273DC,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add fields for each category
            for category, cmds in by_category.items():
                # Format command list
                cmd_list = []
                for cmd in cmds:
                    status = "✅" if cmd.enabled else "❌"
                    trigger_type = f"({cmd.trigger_type})" if cmd.trigger_type != "exact" else ""
                    cmd_list.append(f"{status} **{cmd.trigger}** {trigger_type}")
                    
                # Add field
                embed.add_field(
                    name=f"{category} ({len(cmds)})",
                    value="\n".join(cmd_list) if cmd_list else "No commands",
                    inline=False
                )
            
            # Set footer
            embed.set_footer(text=f"Use !cc info <trigger> for details")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing custom commands: {str(e)}")
            await ctx.send(f"Error listing commands: {str(e)}")
    
    @custom_commands.command(name="info")
    @commands.guild_only()
    async def command_info(self, ctx, trigger: str):
        """
        Show detailed information about a custom command
        
        Args:
            ctx: The command context
            trigger: The trigger word for the command
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Find the command
            cmd = db.session.query(CustomCommand).filter_by(
                guild_id=guild_id,
                trigger=trigger
            ).first()
            
            if not cmd:
                await ctx.send(f"Command `{trigger}` not found")
                return
                
            # Get category if any
            category = "Default"
            if cmd.category_id:
                category_obj = db.session.query(CommandCategory).filter_by(id=cmd.category_id).first()
                if category_obj:
                    category = category_obj.name
            
            # Get usage count
            usage_count = db.session.query(CommandUsage).filter_by(command_id=cmd.id).count()
            
            # Get settings
            settings = json.loads(cmd.settings) if cmd.settings else {}
            
            # Create embed
            embed = discord.Embed(
                title=f"Command: {cmd.trigger}",
                description=f"Type: {cmd.trigger_type}, Category: {category}",
                color=0x3273DC,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add command details
            embed.add_field(name="Status", value="Enabled" if cmd.enabled else "Disabled", inline=True)
            embed.add_field(name="Uses", value=str(usage_count), inline=True)
            embed.add_field(name="Created", value=cmd.created_at.strftime("%Y-%m-%d"), inline=True)
            
            # Add cooldowns if any
            user_cooldown = settings.get("user_cooldown", 0)
            global_cooldown = settings.get("global_cooldown", 0)
            
            if user_cooldown or global_cooldown:
                cooldowns = []
                if user_cooldown:
                    cooldowns.append(f"User: {user_cooldown}s")
                if global_cooldown:
                    cooldowns.append(f"Global: {global_cooldown}s")
                    
                embed.add_field(name="Cooldowns", value=", ".join(cooldowns), inline=True)
            
            # Add response type
            response_type = settings.get("response_type", "text")
            embed.add_field(name="Response Type", value=response_type.title(), inline=True)
            
            # Add content preview (truncated)
            content = cmd.response_content
            if len(content) > 1024:
                content = content[:1021] + "..."
                
            embed.add_field(name="Content Preview", value=f"```\n{content}\n```", inline=False)
            
            # Set footer
            embed.set_footer(text=f"ID: {cmd.id} • Created by {cmd.created_by}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing command info: {str(e)}")
            await ctx.send(f"Error showing command info: {str(e)}")
    
    @custom_commands.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    async def enable_command(self, ctx, trigger: str):
        """
        Enable a custom command
        
        Args:
            ctx: The command context
            trigger: The trigger word for the command
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Find the command
            cmd = db.session.query(CustomCommand).filter_by(
                guild_id=guild_id,
                trigger=trigger
            ).first()
            
            if not cmd:
                await ctx.send(f"Command `{trigger}` not found")
                return
                
            # Update the command
            cmd.enabled = True
            cmd.updated_by = str(ctx.author.id)
            cmd.updated_at = datetime.datetime.utcnow()
            
            db.session.commit()
            
            # Reload guild commands
            await self.cmd_service.reload_guild_commands(guild_id)
            
            # Respond to command
            await ctx.send(f"✅ Command `{trigger}` enabled successfully")
            
        except Exception as e:
            logger.error(f"Error enabling custom command: {str(e)}")
            await ctx.send(f"Error enabling command: {str(e)}")
            db.session.rollback()
    
    @custom_commands.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def disable_command(self, ctx, trigger: str):
        """
        Disable a custom command
        
        Args:
            ctx: The command context
            trigger: The trigger word for the command
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Find the command
            cmd = db.session.query(CustomCommand).filter_by(
                guild_id=guild_id,
                trigger=trigger
            ).first()
            
            if not cmd:
                await ctx.send(f"Command `{trigger}` not found")
                return
                
            # Update the command
            cmd.enabled = False
            cmd.updated_by = str(ctx.author.id)
            cmd.updated_at = datetime.datetime.utcnow()
            
            db.session.commit()
            
            # Reload guild commands
            await self.cmd_service.reload_guild_commands(guild_id)
            
            # Respond to command
            await ctx.send(f"✅ Command `{trigger}` disabled successfully")
            
        except Exception as e:
            logger.error(f"Error disabling custom command: {str(e)}")
            await ctx.send(f"Error disabling command: {str(e)}")
            db.session.rollback()
    
    @custom_commands.command(name="advanced")
    @commands.has_permissions(manage_guild=True)
    async def advanced_command(self, ctx):
        """Direct user to the web dashboard for advanced command creation"""
        await ctx.send(
            "⚡ Advanced command creation is available through the web dashboard:\n"
            "- Visual command builder\n"
            "- Advanced settings and conditions\n"
            "- Templates and variables\n"
            "- Multiple response types\n\n"
            "Visit: https://example.com/dashboard"
        )
    
    @custom_commands.command(name="variables")
    @commands.has_permissions(manage_guild=True)
    async def list_variables(self, ctx):
        """List all custom command variables in the server"""
        guild_id = str(ctx.guild.id)
        
        try:
            # Get all variables for the guild
            variables = db.session.query(CommandVariable).filter_by(guild_id=guild_id).all()
            
            if not variables:
                await ctx.send("No command variables found")
                return
                
            # Create embed
            embed = discord.Embed(
                title="Command Variables",
                description=f"This server has {len(variables)} custom variables",
                color=0x3273DC,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Group variables by type
            var_types = {}
            for var in variables:
                # Determine type
                value = var.value
                if value.isdigit():
                    var_type = "Number"
                elif value.lower() in ("true", "false"):
                    var_type = "Boolean"
                elif value.startswith("{") and value.endswith("}"):
                    try:
                        json.loads(value)
                        var_type = "JSON"
                    except:
                        var_type = "Text"
                else:
                    var_type = "Text"
                    
                if var_type not in var_types:
                    var_types[var_type] = []
                    
                var_types[var_type].append(var)
            
            # Add fields for each type
            for var_type, vars_list in var_types.items():
                # Format variable list
                formatted = []
                for var in vars_list:
                    value = var.value
                    if len(value) > 30:
                        value = value[:27] + "..."
                    formatted.append(f"**{var.name}** = `{value}`")
                    
                # Add field
                embed.add_field(
                    name=f"{var_type} Variables ({len(vars_list)})",
                    value="\n".join(formatted) if formatted else "None",
                    inline=False
                )
            
            # Set footer
            embed.set_footer(text=f"Use !cc var <name> to view a variable's full value")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing command variables: {str(e)}")
            await ctx.send(f"Error listing variables: {str(e)}")
    
    @custom_commands.command(name="var")
    @commands.has_permissions(manage_guild=True)
    async def get_variable(self, ctx, name: str):
        """
        Get the value of a custom command variable
        
        Args:
            ctx: The command context
            name: The variable name
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Get the variable
            value = await self.cmd_service.get_command_variable(guild_id, name)
            
            if value is None:
                await ctx.send(f"Variable `{name}` not found")
                return
                
            # Create embed
            embed = discord.Embed(
                title=f"Variable: {name}",
                color=0x3273DC,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Determine value type
            if value.isdigit():
                var_type = "Number"
            elif value.lower() in ("true", "false"):
                var_type = "Boolean"
            elif value.startswith("{") and value.endswith("}"):
                try:
                    json.loads(value)
                    var_type = "JSON"
                except:
                    var_type = "Text"
            else:
                var_type = "Text"
                
            embed.add_field(name="Type", value=var_type, inline=False)
            
            # Format the value
            if len(value) > 1024:
                value = value[:1021] + "..."
                
            embed.add_field(name="Value", value=f"```\n{value}\n```", inline=False)
            
            # Set footer
            embed.set_footer(text="Use !cc setvar to update this variable")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting command variable: {str(e)}")
            await ctx.send(f"Error getting variable: {str(e)}")
    
    @custom_commands.command(name="setvar")
    @commands.has_permissions(manage_guild=True)
    async def set_variable(self, ctx, name: str, *, value: str):
        """
        Set the value of a custom command variable
        
        Args:
            ctx: The command context
            name: The variable name
            value: The variable value
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Set the variable
            await self.cmd_service.set_command_variable(guild_id, name, value)
            
            # Respond to command
            await ctx.send(f"✅ Variable `{name}` set successfully")
            
        except Exception as e:
            logger.error(f"Error setting command variable: {str(e)}")
            await ctx.send(f"Error setting variable: {str(e)}")
    
    @custom_commands.command(name="delvar")
    @commands.has_permissions(manage_guild=True)
    async def delete_variable(self, ctx, name: str):
        """
        Delete a custom command variable
        
        Args:
            ctx: The command context
            name: The variable name
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Find the variable
            var = db.session.query(CommandVariable).filter_by(
                guild_id=guild_id,
                name=name
            ).first()
            
            if not var:
                await ctx.send(f"Variable `{name}` not found")
                return
                
            # Delete the variable
            db.session.delete(var)
            db.session.commit()
            
            # Remove from cache
            if guild_id in self.cmd_service.variables_cache and name in self.cmd_service.variables_cache[guild_id]:
                del self.cmd_service.variables_cache[guild_id][name]
            
            # Respond to command
            await ctx.send(f"✅ Variable `{name}` deleted successfully")
            
        except Exception as e:
            logger.error(f"Error deleting command variable: {str(e)}")
            await ctx.send(f"Error deleting variable: {str(e)}")
            db.session.rollback()
    
    @custom_commands.command(name="templates")
    @commands.guild_only()
    async def list_templates(self, ctx):
        """List available command templates"""
        try:
            # Get templates
            templates = self.cmd_service.command_templates
            
            if not templates:
                await ctx.send("No command templates available")
                return
                
            # Group templates by category
            by_category = {}
            for template in templates:
                category = template.category or "General"
                if category not in by_category:
                    by_category[category] = []
                    
                by_category[category].append(template)
            
            # Create embed
            embed = discord.Embed(
                title="Command Templates",
                description="Use these templates to quickly create advanced commands",
                color=0x3273DC,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add fields for each category
            for category, templates_list in by_category.items():
                # Format template list
                formatted = []
                for template in templates_list:
                    complexity = "⭐" * min(template.complexity, 5)
                    formatted.append(f"**{template.name}** {complexity}")
                    
                # Add field
                embed.add_field(
                    name=f"{category} ({len(templates_list)})",
                    value="\n".join(formatted) if formatted else "None",
                    inline=False
                )
            
            # Set footer
            embed.set_footer(text=f"Use !cc template <name> to view template details")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing command templates: {str(e)}")
            await ctx.send(f"Error listing templates: {str(e)}")
    
    @custom_commands.command(name="template")
    @commands.guild_only()
    async def get_template(self, ctx, *, name: str):
        """
        Get details for a specific command template
        
        Args:
            ctx: The command context
            name: The template name
        """
        try:
            # Find the template
            template = None
            for t in self.cmd_service.command_templates:
                if t.name.lower() == name.lower():
                    template = t
                    break
                    
            if not template:
                await ctx.send(f"Template `{name}` not found")
                return
                
            # Create embed
            embed = discord.Embed(
                title=f"Template: {template.name}",
                description=template.description,
                color=0x3273DC,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add template details
            embed.add_field(name="Category", value=template.category or "General", inline=True)
            embed.add_field(name="Complexity", value="⭐" * min(template.complexity, 5), inline=True)
            
            # Add usage instructions
            if template.usage_instructions:
                embed.add_field(name="Usage", value=template.usage_instructions, inline=False)
            
            # Add example code
            if template.example_code:
                code = template.example_code
                if len(code) > 1024:
                    code = code[:1021] + "..."
                    
                embed.add_field(name="Example", value=f"```\n{code}\n```", inline=False)
            
            # Set footer
            embed.set_footer(text=f"Use !cc use-template {template.name} <trigger> to use this template")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting command template: {str(e)}")
            await ctx.send(f"Error getting template: {str(e)}")
    
    @custom_commands.command(name="use-template")
    @commands.has_permissions(manage_guild=True)
    async def use_template(self, ctx, template_name: str, trigger: str):
        """
        Create a new command from a template
        
        Args:
            ctx: The command context
            template_name: The name of the template to use
            trigger: The trigger for the new command
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Find the template
            template = None
            for t in self.cmd_service.command_templates:
                if t.name.lower() == template_name.lower():
                    template = t
                    break
                    
            if not template:
                await ctx.send(f"Template `{template_name}` not found")
                return
                
            # Check if trigger already exists
            existing = db.session.query(CustomCommand).filter_by(
                guild_id=guild_id,
                trigger=trigger
            ).first()
            
            if existing:
                await ctx.send(f"Command with trigger `{trigger}` already exists")
                return
                
            # Create new command
            new_cmd = CustomCommand(
                guild_id=guild_id,
                trigger=trigger,
                trigger_type=template.trigger_type or "exact",
                response_content=template.code,
                settings=template.settings,
                created_by=str(ctx.author.id),
                created_at=datetime.datetime.utcnow(),
                enabled=True
            )
            
            db.session.add(new_cmd)
            db.session.commit()
            
            # Reload guild commands
            await self.cmd_service.reload_guild_commands(guild_id)
            
            # Respond to command
            await ctx.send(
                f"✅ Command `{trigger}` created from template **{template.name}**\n"
                f"You may want to edit it to customize for your needs."
            )
            
        except Exception as e:
            logger.error(f"Error using command template: {str(e)}")
            await ctx.send(f"Error using template: {str(e)}")
            db.session.rollback()
    
    @custom_commands.command(name="suggest")
    @commands.has_permissions(manage_guild=True)
    async def suggest_command(self, ctx, *, description: str):
        """
        Get an AI-generated command suggestion
        
        Args:
            ctx: The command context
            description: Description of what the command should do
        """
        try:
            # Get suggestion from AI service
            await ctx.send("🤖 Generating command suggestion... This may take a moment.")
            
            suggestion = await generate_command_suggestion(description)
            
            if not suggestion:
                await ctx.send("❌ Failed to generate a suggestion. Please try again.")
                return
                
            # Format the response
            embed = discord.Embed(
                title="Command Suggestion",
                description=f"Based on: {description}",
                color=0x3273DC,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add trigger
            embed.add_field(name="Suggested Trigger", value=suggestion.get("trigger", "custom-command"), inline=True)
            
            # Add trigger type
            embed.add_field(name="Trigger Type", value=suggestion.get("trigger_type", "exact"), inline=True)
            
            # Add response type
            embed.add_field(name="Response Type", value=suggestion.get("response_type", "text"), inline=True)
            
            # Add content
            content = suggestion.get("content", "")
            if len(content) > 1024:
                content = content[:1021] + "..."
                
            embed.add_field(name="Content", value=f"```\n{content}\n```", inline=False)
            
            # Add usage instructions
            if "usage" in suggestion:
                embed.add_field(name="Usage", value=suggestion["usage"], inline=False)
            
            # Set footer
            embed.set_footer(text="Use !cc add <trigger> <response> to create this command")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error suggesting command: {str(e)}")
            await ctx.send(f"Error suggesting command: {str(e)}")

def setup(bot):
    # Create and initialize the custom commands service
    cmd_service = AdvancedCustomCommandsSystem(bot)
    bot.loop.create_task(cmd_service.initialize())
    
    # Register the commands
    bot.add_cog(CustomCommandsCommands(bot, cmd_service))
    
    # Make the service available to other cogs
    bot.custom_commands_service = cmd_service