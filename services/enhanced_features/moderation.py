"""
AstroBot AI Enhanced Moderation System
A powerful, AI-driven moderation system with advanced features.
"""
import json
import logging
import re
import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import defaultdict

import discord
from discord.ext import commands
import asyncio

from app import db
from models import (
    ModerationAction, ModTrigger, AutoModRule, 
    AutoModTrigger, UserTrustScore, ModLog
)
from services.ai_service import analyze_context, detect_toxic_content
from utils.embed_creator import create_moderation_embed

logger = logging.getLogger(__name__)

class AdvancedModerationSystem:
    """
    Enhanced moderation system with AI-powered decision making, user behavior analytics,
    and context-sensitive auto-moderation.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.warning_levels = {
            "low": {"color": 0xFFDD57, "action": None, "threshold": 1},
            "medium": {"color": 0xFFA500, "action": "mute", "threshold": 3},
            "high": {"color": 0xFF3860, "action": "kick", "threshold": 5},
            "severe": {"color": 0x9D0000, "action": "ban", "threshold": 7}
        }
        self.user_warnings = defaultdict(int)  # user_id: warning_count
        self.action_handlers = {
            "warn": self.handle_warning,
            "mute": self.handle_mute,
            "kick": self.handle_kick,
            "ban": self.handle_ban,
            "delete": self.handle_delete,
            "timeout": self.handle_timeout,
        }
        self.mod_log_channels = {}  # guild_id: channel_id
        self.trust_score_cache = {}  # user_id: trust_score
        
        # Regex patterns for common auto-mod triggers
        self.patterns = {
            "invite": re.compile(r"discord(?:\.gg|app\.com\/invite|\.com\/invite)\/([a-zA-Z0-9\-]+)"),
            "url": re.compile(r"https?:\/\/[^\s<]+[^<.,:;\"\')\]\s]"),
            "caps": re.compile(r"[A-Z]{10,}"),
            "spam": re.compile(r"(.)\1{9,}"),
            "emoji_spam": re.compile(r"(<a?:[a-zA-Z0-9_]+:[0-9]+>){5,}"),
            "mention_spam": re.compile(r"(<@!?[0-9]+>){5,}")
        }
        
    async def initialize(self):
        """Initialize the moderation system on bot startup"""
        # Load existing mod log channels
        await self.load_mod_log_channels()
        # Initialize auto-mod rules
        await self.initialize_automod_rules()
        # Register listeners
        self.bot.add_listener(self.on_message, "on_message")
        self.bot.add_listener(self.on_message_delete, "on_message_delete")
        self.bot.add_listener(self.on_message_edit, "on_message_edit")
        self.bot.add_listener(self.on_member_join, "on_member_join")
        self.bot.add_listener(self.on_member_remove, "on_member_remove")
        logger.info("Advanced Moderation System initialized")
        
    async def load_mod_log_channels(self):
        """Load configured moderation log channels from database"""
        try:
            # Query database for all configured mod log channels
            query = db.session.query(ModLog).all()
            for log in query:
                self.mod_log_channels[log.guild_id] = log.channel_id
            logger.info(f"Loaded {len(self.mod_log_channels)} moderation log channels")
        except Exception as e:
            logger.error(f"Error loading moderation log channels: {str(e)}")
    
    async def initialize_automod_rules(self):
        """Initialize auto-moderation rules from database"""
        try:
            # This would initialize auto-mod rules from the database
            # For now, we'll use default behavior
            logger.info("Auto-moderation rules initialized")
        except Exception as e:
            logger.error(f"Error initializing auto-mod rules: {str(e)}")
    
    async def get_user_trust_score(self, user_id: str, guild_id: str) -> float:
        """
        Get a user's trust score, which affects auto-mod sensitivity
        A higher score means more trusted (less strict auto-mod)
        
        Args:
            user_id: The user's Discord ID
            guild_id: The guild ID where trust is being evaluated
            
        Returns:
            float: Trust score between 0.0 (untrusted) and 1.0 (fully trusted)
        """
        cache_key = f"{user_id}:{guild_id}"
        
        # Check if we have a cached value
        if cache_key in self.trust_score_cache:
            return self.trust_score_cache[cache_key]
            
        try:
            # Query the user's trust score
            trust_record = db.session.query(UserTrustScore).filter_by(
                user_id=user_id,
                guild_id=guild_id
            ).first()
            
            if trust_record:
                score = trust_record.score
            else:
                # Default score for new users
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    return 0.5  # Default mid-level trust
                
                member = guild.get_member(int(user_id))
                if not member:
                    return 0.5  # Default mid-level trust
                
                # For new users, calculate initial score based on account age,
                # whether they have a profile picture, etc.
                days_on_discord = (datetime.datetime.utcnow() - member.created_at).days
                days_in_server = (datetime.datetime.utcnow() - member.joined_at).days if member.joined_at else 0
                
                # Start with a base score
                score = 0.5
                
                # Account older than 30 days gets a boost
                if days_on_discord > 30:
                    score += min(0.1, days_on_discord / 1000)  # Cap at 0.1
                    
                # In server for more than 7 days gets a boost
                if days_in_server > 7:
                    score += min(0.1, days_in_server / 500)  # Cap at 0.1
                    
                # Has a profile picture
                if not member.default_avatar_url:
                    score += 0.05
                    
                # Has roles in the server (excluding everyone role)
                if len(member.roles) > 1:
                    score += min(0.1, (len(member.roles) - 1) * 0.02)  # Cap at 0.1
                
                # Create a new trust score record
                new_trust = UserTrustScore(
                    user_id=user_id,
                    guild_id=guild_id,
                    score=score,
                    last_updated=datetime.datetime.utcnow()
                )
                db.session.add(new_trust)
                db.session.commit()
            
            # Cache the result
            self.trust_score_cache[cache_key] = score
            return score
            
        except Exception as e:
            logger.error(f"Error getting user trust score: {str(e)}")
            return 0.5  # Default mid-level trust on error
    
    async def update_trust_score(self, user_id: str, guild_id: str, adjustment: float):
        """
        Update a user's trust score
        
        Args:
            user_id: The user's Discord ID
            guild_id: The guild ID where trust is being evaluated
            adjustment: Amount to adjust the score (-1.0 to 1.0)
        """
        try:
            cache_key = f"{user_id}:{guild_id}"
            
            # Get current score
            current_score = await self.get_user_trust_score(user_id, guild_id)
            
            # Calculate new score (bounded between 0 and 1)
            new_score = max(0.0, min(1.0, current_score + adjustment))
            
            # Update database
            trust_record = db.session.query(UserTrustScore).filter_by(
                user_id=user_id,
                guild_id=guild_id
            ).first()
            
            if trust_record:
                trust_record.score = new_score
                trust_record.last_updated = datetime.datetime.utcnow()
            else:
                new_trust = UserTrustScore(
                    user_id=user_id,
                    guild_id=guild_id,
                    score=new_score,
                    last_updated=datetime.datetime.utcnow()
                )
                db.session.add(new_trust)
            
            db.session.commit()
            
            # Update cache
            self.trust_score_cache[cache_key] = new_score
            
            logger.info(f"Updated trust score for user {user_id} in guild {guild_id}: {current_score} -> {new_score}")
            
        except Exception as e:
            logger.error(f"Error updating user trust score: {str(e)}")
    
    async def on_message(self, message: discord.Message):
        """Handle message events for moderation purposes"""
        # Ignore messages from bots
        if message.author.bot:
            return
            
        # Ignore DMs
        if not message.guild:
            return
            
        # Check auto-moderation rules
        await self.check_auto_moderation(message)
    
    async def on_message_delete(self, message: discord.Message):
        """Handle message deletion events"""
        # Skip bot messages
        if message.author.bot:
            return
            
        # Log message deletions if configured
        await self.log_message_deletion(message)
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Handle message edit events"""
        # Skip bot messages
        if before.author.bot:
            return
            
        # Check auto-moderation on edited message
        await self.check_auto_moderation(after)
        
        # Log message edits if configured
        await self.log_message_edit(before, after)
    
    async def on_member_join(self, member: discord.Member):
        """Handle member join events"""
        # Check ban evasion
        await self.check_ban_evasion(member)
        
        # Log member join
        await self.log_member_join(member)
    
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave events"""
        # Log member leave
        await self.log_member_leave(member)
    
    async def check_auto_moderation(self, message: discord.Message):
        """
        Check a message against auto-moderation rules
        
        Args:
            message: The Discord message to check
        """
        # Get user trust score
        trust_score = await self.get_user_trust_score(
            str(message.author.id), 
            str(message.guild.id)
        )
        
        # Get auto-mod rules for this guild
        try:
            rules = db.session.query(AutoModRule).filter_by(
                guild_id=str(message.guild.id),
                enabled=True
            ).order_by(AutoModRule.priority).all()
        except Exception as e:
            logger.error(f"Error fetching auto-mod rules: {str(e)}")
            rules = []
        
        # No rules to process
        if not rules:
            # Check basic patterns anyway
            basic_violations = await self.check_basic_patterns(message, trust_score)
            if basic_violations:
                await self.handle_automod_violation(message, basic_violations)
            return
        
        # Process each rule
        for rule in rules:
            # Skip rules that don't apply to this channel
            if rule.channel_list and str(message.channel.id) not in rule.channel_list.split(','):
                continue
                
            # Skip rules that don't apply to this user's roles
            if rule.exempt_roles:
                exempt_role_ids = rule.exempt_roles.split(',')
                if any(str(role.id) in exempt_role_ids for role in message.author.roles):
                    continue
            
            # Process rule conditions
            rule_triggered, violation_type = await self.check_rule_conditions(rule, message, trust_score)
            
            if rule_triggered:
                # Take the configured action
                await self.handle_automod_rule_trigger(rule, message, violation_type)
                
                # Record the trigger event
                self.record_automod_trigger(rule, message, violation_type)
                
                # If rule has a stop flag, don't process further rules
                if rule.stop_processing:
                    break
    
    async def check_basic_patterns(self, message: discord.Message, trust_score: float) -> List[str]:
        """
        Check message against basic auto-mod patterns
        
        Args:
            message: The Discord message to check
            trust_score: The user's trust score
            
        Returns:
            List[str]: List of violation types detected
        """
        violations = []
        content = message.content
        
        # Skip checks for high-trust users
        if trust_score > 0.8:
            return violations
        
        # Check for Discord invites
        if self.patterns["invite"].search(content):
            violations.append("discord_invite")
            
        # Check for excessive caps
        if self.patterns["caps"].search(content) and len(content) > 20:
            violations.append("excessive_caps")
            
        # Check for character spam
        if self.patterns["spam"].search(content):
            violations.append("character_spam")
            
        # Check for emoji spam
        if self.patterns["emoji_spam"].search(content):
            violations.append("emoji_spam")
            
        # Check for mention spam
        if self.patterns["mention_spam"].search(content) or len(message.mentions) > 5:
            violations.append("mention_spam")
            
        # Use AI to detect toxic content for more nuanced checks
        if len(content) > 20 and await detect_toxic_content(content):
            violations.append("toxic_content")
        
        return violations
    
    async def check_rule_conditions(
        self, 
        rule: AutoModRule, 
        message: discord.Message,
        trust_score: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a message violates a specific auto-mod rule
        
        Args:
            rule: The auto-mod rule to check
            message: The Discord message to check
            trust_score: User's trust score (0.0-1.0)
            
        Returns:
            Tuple[bool, Optional[str]]: Whether rule was triggered and violation type
        """
        try:
            # Load rule triggers
            try:
                # Parse the rule settings
                settings = json.loads(rule.rule_settings)
                
                # Skip processing if rule is beyond the user's trust threshold
                # (allow trusted users to bypass some rules)
                if "min_trust_score" in settings and trust_score < settings["min_trust_score"]:
                    return False, None
                    
                # Process different rule types
                rule_type = rule.rule_type
                
                if rule_type == "regex":
                    # Regular expression pattern matching
                    if "pattern" in settings:
                        pattern = re.compile(settings["pattern"], re.IGNORECASE)
                        if pattern.search(message.content):
                            return True, "regex_match"
                            
                elif rule_type == "word_filter":
                    # Check for filtered words
                    if "words" in settings:
                        words = [word.lower() for word in settings["words"]]
                        content_lower = message.content.lower()
                        
                        for word in words:
                            # Check if the word is surrounded by word boundaries (not part of another word)
                            word_pattern = r'\b' + re.escape(word) + r'\b'
                            if re.search(word_pattern, content_lower):
                                return True, "filtered_word"
                                
                elif rule_type == "link_filter":
                    # Check for filtered links/domains
                    if "domains" in settings:
                        for url_match in self.patterns["url"].finditer(message.content):
                            url = url_match.group(0)
                            for domain in settings["domains"]:
                                if domain.lower() in url.lower():
                                    return True, "filtered_link"
                                    
                elif rule_type == "spam_detection":
                    # More advanced spam detection logic
                    if "message_similarity_threshold" in settings:
                        # This would compare against recent messages from the same user
                        # Simplified implementation for now
                        pass
                        
                elif rule_type == "mention_limit":
                    # Check for excessive mentions
                    if "max_mentions" in settings:
                        max_mentions = int(settings["max_mentions"])
                        mention_count = len(message.mentions) + len(message.role_mentions)
                        if mention_count > max_mentions:
                            return True, "excessive_mentions"
                            
                elif rule_type == "attachment_filter":
                    # Filter based on attachments
                    if "allowed_extensions" in settings and message.attachments:
                        allowed_exts = [ext.lower() for ext in settings["allowed_extensions"]]
                        for attachment in message.attachments:
                            filename = attachment.filename.lower()
                            ext = filename.split('.')[-1] if '.' in filename else ""
                            if ext not in allowed_exts:
                                return True, "disallowed_attachment"
                                
                elif rule_type == "ai_toxic_content":
                    # Use AI to detect toxic content
                    if len(message.content) > 10:
                        is_toxic = await detect_toxic_content(message.content)
                        if is_toxic:
                            return True, "toxic_content"
                            
            except Exception as e:
                logger.error(f"Error checking rule conditions: {str(e)}")
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking rule conditions: {str(e)}")
            return False, None
    
    async def handle_automod_violation(self, message: discord.Message, violations: List[str]):
        """
        Handle basic pattern violations with default actions
        
        Args:
            message: The Discord message with violations
            violations: List of violation types
        """
        if not violations:
            return
            
        # Define default actions for violations
        actions = {
            "discord_invite": {"action": "delete", "warning": "low"},
            "excessive_caps": {"action": "delete", "warning": "low"},
            "character_spam": {"action": "delete", "warning": "low"},
            "emoji_spam": {"action": "delete", "warning": "low"},
            "mention_spam": {"action": "delete", "warning": "medium"},
            "toxic_content": {"action": "delete", "warning": "medium"}
        }
        
        # Process the first violation (typically only one would trigger anyway)
        violation = violations[0]
        if violation in actions:
            action_config = actions[violation]
            
            # Delete the message if that's the action
            if action_config["action"] == "delete":
                try:
                    await message.delete()
                except Exception as e:
                    logger.error(f"Error deleting message: {str(e)}")
                    
            # Issue a warning if configured
            if "warning" in action_config:
                warning_level = action_config["warning"]
                await self.issue_warning(
                    user_id=str(message.author.id),
                    guild_id=str(message.guild.id),
                    moderator_id=str(self.bot.user.id),  # Bot is the moderator
                    reason=f"Auto-mod: {violation.replace('_', ' ').title()}",
                    warning_level=warning_level,
                    channel_id=str(message.channel.id),
                    message_id=str(message.id)
                )
                
            # Record the auto-mod trigger
            self.record_basic_automod_trigger(message, violation)
    
    async def handle_automod_rule_trigger(
        self, 
        rule: AutoModRule, 
        message: discord.Message,
        violation_type: str
    ):
        """
        Handle an auto-mod rule trigger with the configured action
        
        Args:
            rule: The triggered rule
            message: The Discord message that triggered the rule
            violation_type: The type of violation that occurred
        """
        try:
            # Parse rule settings
            settings = json.loads(rule.rule_settings)
            action = settings.get("action", "none")
            
            # Execute the appropriate action
            if action == "delete":
                try:
                    await message.delete()
                except Exception as e:
                    logger.error(f"Error deleting message: {str(e)}")
                    
            elif action == "warn":
                warning_level = settings.get("warning_level", "low")
                await self.issue_warning(
                    user_id=str(message.author.id),
                    guild_id=str(message.guild.id),
                    moderator_id=str(self.bot.user.id),  # Bot is the moderator
                    reason=f"Auto-mod: {rule.name}",
                    warning_level=warning_level,
                    channel_id=str(message.channel.id),
                    message_id=str(message.id)
                )
                
            elif action == "mute":
                duration = settings.get("duration_minutes", 10)
                await self.handle_mute(
                    guild_id=str(message.guild.id),
                    user_id=str(message.author.id),
                    moderator_id=str(self.bot.user.id),
                    reason=f"Auto-mod: {rule.name}",
                    duration_minutes=duration
                )
                
            elif action == "kick":
                await self.handle_kick(
                    guild_id=str(message.guild.id),
                    user_id=str(message.author.id),
                    moderator_id=str(self.bot.user.id),
                    reason=f"Auto-mod: {rule.name}"
                )
                
            elif action == "ban":
                duration = settings.get("duration_days", None)  # None means permanent
                await self.handle_ban(
                    guild_id=str(message.guild.id),
                    user_id=str(message.author.id),
                    moderator_id=str(self.bot.user.id),
                    reason=f"Auto-mod: {rule.name}",
                    duration_days=duration
                )
                
            # Send notification if configured
            if settings.get("send_notification", False):
                notification_channel_id = settings.get("notification_channel_id")
                if notification_channel_id:
                    await self.send_automod_notification(
                        rule, message, violation_type, notification_channel_id
                    )
                    
        except Exception as e:
            logger.error(f"Error handling auto-mod rule trigger: {str(e)}")
    
    async def send_automod_notification(
        self, 
        rule: AutoModRule, 
        message: discord.Message,
        violation_type: str,
        channel_id: str
    ):
        """
        Send a notification about an auto-mod trigger
        
        Args:
            rule: The triggered rule
            message: The message that triggered the rule
            violation_type: The type of violation
            channel_id: Channel ID to send notification to
        """
        try:
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return
                
            # Create embed for the notification
            embed = create_moderation_embed(
                title="Auto-Moderation Triggered",
                description=f"Rule **{rule.name}** was triggered",
                user=str(message.author),
                user_id=str(message.author.id),
                reason=f"Violation type: {violation_type}",
                color=0xFF3860  # Red color for warnings
            )
            
            # Add message content (truncate if too long)
            content = message.content
            if len(content) > 1024:
                content = content[:1021] + "..."
            embed.add_field(name="Message Content", value=content, inline=False)
            
            # Add channel information
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            
            # Add timestamp
            embed.timestamp = datetime.datetime.utcnow()
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending auto-mod notification: {str(e)}")
    
    def record_automod_trigger(
        self, 
        rule: AutoModRule, 
        message: discord.Message,
        violation_type: str
    ):
        """
        Record an auto-mod rule trigger in the database
        
        Args:
            rule: The rule that was triggered
            message: The Discord message that triggered the rule
            violation_type: The type of violation
        """
        try:
            # Create new trigger record
            trigger = AutoModTrigger(
                rule_id=rule.id,
                guild_id=str(message.guild.id),
                user_id=str(message.author.id),
                channel_id=str(message.channel.id),
                message_id=str(message.id) if message.id else None,
                trigger_type=violation_type,
                content_snippet=message.content[:255] if message.content else None,  # Truncate to 255 chars
                action_taken=rule.rule_settings.get("action", "none"),
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(trigger)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error recording auto-mod trigger: {str(e)}")
            db.session.rollback()
    
    def record_basic_automod_trigger(self, message: discord.Message, violation_type: str):
        """
        Record a basic auto-mod trigger in the database
        
        Args:
            message: The Discord message with the violation
            violation_type: The type of violation detected
        """
        try:
            # Get the default action for this violation
            actions = {
                "discord_invite": "delete",
                "excessive_caps": "delete",
                "character_spam": "delete",
                "emoji_spam": "delete",
                "mention_spam": "delete",
                "toxic_content": "delete"
            }
            action = actions.get(violation_type, "none")
            
            # Create new trigger record
            trigger = ModTrigger(
                guild_id=str(message.guild.id),
                user_id=str(message.author.id),
                channel_id=str(message.channel.id),
                message_id=str(message.id) if message.id else None,
                trigger_type=violation_type,
                content_snippet=message.content[:255] if message.content else None,  # Truncate to 255 chars
                action_taken=action,
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(trigger)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error recording basic auto-mod trigger: {str(e)}")
            db.session.rollback()
    
    async def issue_warning(
        self,
        user_id: str,
        guild_id: str,
        moderator_id: str,
        reason: str,
        warning_level: str = "low",
        channel_id: Optional[str] = None,
        message_id: Optional[str] = None
    ):
        """
        Issue a warning to a user and potentially take automated action
        based on warning thresholds
        
        Args:
            user_id: The Discord ID of the user being warned
            guild_id: The Discord ID of the guild
            moderator_id: The Discord ID of the moderator issuing the warning
            reason: The reason for the warning
            warning_level: The severity level of the warning (low, medium, high, severe)
            channel_id: Optional channel ID where the warning was triggered
            message_id: Optional message ID that triggered the warning
        """
        # Increment user warning count
        user_key = f"{user_id}:{guild_id}"
        self.user_warnings[user_key] += 1
        warning_count = self.user_warnings[user_key]
        
        try:
            # Create warning record in database
            warning = ModerationAction(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type="warning",
                reason=reason,
                severity=warning_level,
                channel_id=channel_id,
                message_id=message_id,
                active=True,
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(warning)
            db.session.commit()
            
            # Get warning level configuration
            level_config = self.warning_levels.get(warning_level, self.warning_levels["low"])
            threshold = level_config["threshold"]
            action = level_config["action"]
            
            # Negatively adjust trust score
            adjustment = {
                "low": -0.02,
                "medium": -0.05,
                "high": -0.1,
                "severe": -0.2
            }.get(warning_level, -0.02)
            
            await self.update_trust_score(user_id, guild_id, adjustment)
            
            # Get guild and member objects
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                return
                
            member = guild.get_member(int(user_id))
            if not member:
                logger.error(f"Could not find member {user_id} in guild {guild_id}")
                return
                
            # Try to DM the user about the warning
            dm_sent = False
            try:
                # Create warning embed
                embed = create_moderation_embed(
                    title=f"{warning_level.title()} Warning",
                    description=f"You have received a warning in **{guild.name}**",
                    moderator=guild.get_member(int(moderator_id)).display_name if guild.get_member(int(moderator_id)) else "System",
                    reason=reason,
                    color=level_config["color"],
                    include_timestamp=True
                )
                
                await member.send(embed=embed)
                dm_sent = True
            except Exception as e:
                logger.error(f"Error sending DM to warned user: {str(e)}")
            
            # Log the warning
            await self.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action="warning",
                reason=reason,
                dm_sent=dm_sent
            )
            
            # Check for automated action if warning threshold is reached
            if warning_count >= threshold and action:
                # Take the configured action
                await self.action_handlers[action](
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=moderator_id,
                    reason=f"Automated action after {warning_count} warnings"
                )
                
        except Exception as e:
            logger.error(f"Error issuing warning: {str(e)}")
            db.session.rollback()
    
    async def handle_warning(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str,
        warning_level: str = "low",
        **kwargs
    ):
        """
        Handle warning action
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator
            reason: The reason for the action
            warning_level: The severity level of the warning
            **kwargs: Additional keyword arguments
        """
        await self.issue_warning(
            user_id=user_id,
            guild_id=guild_id,
            moderator_id=moderator_id,
            reason=reason,
            warning_level=warning_level
        )
    
    async def handle_mute(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str,
        duration_minutes: Optional[int] = None,
        **kwargs
    ):
        """
        Handle mute action
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator
            reason: The reason for the action
            duration_minutes: Optional duration of the mute in minutes (None for indefinite)
            **kwargs: Additional keyword arguments
        """
        try:
            # Get guild and member
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                return
                
            member = guild.get_member(int(user_id))
            if not member:
                logger.error(f"Could not find member {user_id} in guild {guild_id}")
                return
                
            # Calculate end time if duration is provided
            end_time = None
            if duration_minutes:
                end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration_minutes)
            
            # Mute the user - try to use timeout feature
            try:
                if end_time:
                    await member.timeout(duration=datetime.timedelta(minutes=duration_minutes), reason=reason)
                else:
                    await member.timeout(reason=reason)
            except Exception as timeout_error:
                logger.error(f"Error applying timeout: {str(timeout_error)}")
                # Fall back to role-based mute if timeout fails
                try:
                    # Attempt to find or create a "Muted" role with appropriate permissions
                    muted_role = discord.utils.get(guild.roles, name="Muted")
                    if not muted_role:
                        # Create a new Muted role
                        permissions = discord.Permissions()
                        permissions.update(send_messages=False, speak=False)
                        muted_role = await guild.create_role(name="Muted", permissions=permissions)
                        
                        # Update channel permissions for this role
                        for channel in guild.channels:
                            try:
                                await channel.set_permissions(
                                    muted_role,
                                    send_messages=False,
                                    speak=False,
                                    add_reactions=False
                                )
                            except Exception as e:
                                logger.error(f"Error setting permissions for channel {channel.name}: {str(e)}")
                    
                    # Assign the muted role
                    await member.add_roles(muted_role, reason=reason)
                    
                except Exception as role_error:
                    logger.error(f"Error applying role-based mute: {str(role_error)}")
                    return
            
            # Record action in database
            mute_action = ModerationAction(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type="mute",
                reason=reason,
                expires_at=end_time,
                active=True,
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(mute_action)
            db.session.commit()
            
            # Try to DM the user
            dm_sent = False
            try:
                # Create mute embed
                duration_text = f"for {duration_minutes} minutes" if duration_minutes else "indefinitely"
                embed = create_moderation_embed(
                    title="You Have Been Muted",
                    description=f"You have been muted in **{guild.name}** {duration_text}",
                    moderator=guild.get_member(int(moderator_id)).display_name if guild.get_member(int(moderator_id)) else "System",
                    reason=reason,
                    color=0xFF3860,  # Red color
                    include_timestamp=True
                )
                
                await member.send(embed=embed)
                dm_sent = True
            except Exception as e:
                logger.error(f"Error sending DM to muted user: {str(e)}")
            
            # Log the action
            await self.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action="mute",
                reason=reason,
                duration=duration_minutes,
                dm_sent=dm_sent
            )
            
            # Update user trust score
            await self.update_trust_score(user_id, guild_id, -0.1)
            
        except Exception as e:
            logger.error(f"Error handling mute action: {str(e)}")
            db.session.rollback()
    
    async def handle_kick(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str,
        **kwargs
    ):
        """
        Handle kick action
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator
            reason: The reason for the action
            **kwargs: Additional keyword arguments
        """
        try:
            # Get guild and member
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                return
                
            member = guild.get_member(int(user_id))
            if not member:
                logger.error(f"Could not find member {user_id} in guild {guild_id}")
                return
            
            # Try to DM the user before kicking
            dm_sent = False
            try:
                # Create kick embed
                embed = create_moderation_embed(
                    title="You Have Been Kicked",
                    description=f"You have been kicked from **{guild.name}**",
                    moderator=guild.get_member(int(moderator_id)).display_name if guild.get_member(int(moderator_id)) else "System",
                    reason=reason,
                    color=0xFF3860,  # Red color
                    include_timestamp=True
                )
                
                await member.send(embed=embed)
                dm_sent = True
            except Exception as e:
                logger.error(f"Error sending DM to kicked user: {str(e)}")
            
            # Kick the member
            await member.kick(reason=reason)
            
            # Record action in database
            kick_action = ModerationAction(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type="kick",
                reason=reason,
                active=False,  # Kick is not an "active" state
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(kick_action)
            db.session.commit()
            
            # Log the action
            await self.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action="kick",
                reason=reason,
                dm_sent=dm_sent
            )
            
            # Update user trust score substantially
            await self.update_trust_score(user_id, guild_id, -0.3)
            
        except Exception as e:
            logger.error(f"Error handling kick action: {str(e)}")
            db.session.rollback()
    
    async def handle_ban(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str,
        duration_days: Optional[int] = None,  # None means permanent
        delete_message_days: int = 1,
        **kwargs
    ):
        """
        Handle ban action
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator
            reason: The reason for the action
            duration_days: Optional duration of the ban in days (None for permanent)
            delete_message_days: Number of days of messages to delete (0-7)
            **kwargs: Additional keyword arguments
        """
        try:
            # Get guild
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                return
            
            # Try to get member (they might not be in the guild)
            member = guild.get_member(int(user_id))
            
            # Calculate end time if duration is provided
            end_time = None
            if duration_days:
                end_time = datetime.datetime.utcnow() + datetime.timedelta(days=duration_days)
            
            # Try to DM the user before banning if they're in the guild
            dm_sent = False
            if member:
                try:
                    # Create ban embed
                    duration_text = f"for {duration_days} days" if duration_days else "permanently"
                    embed = create_moderation_embed(
                        title="You Have Been Banned",
                        description=f"You have been banned from **{guild.name}** {duration_text}",
                        moderator=guild.get_member(int(moderator_id)).display_name if guild.get_member(int(moderator_id)) else "System",
                        reason=reason,
                        color=0xFF3860,  # Red color
                        include_timestamp=True
                    )
                    
                    await member.send(embed=embed)
                    dm_sent = True
                except Exception as e:
                    logger.error(f"Error sending DM to banned user: {str(e)}")
            
            # Ban the user
            await guild.ban(
                discord.Object(id=int(user_id)),
                reason=reason,
                delete_message_days=min(delete_message_days, 7)  # Discord limits to 7 days
            )
            
            # Record action in database
            ban_action = ModerationAction(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type="ban",
                reason=reason,
                expires_at=end_time,
                active=True,
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(ban_action)
            db.session.commit()
            
            # Log the action
            await self.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action="ban",
                reason=reason,
                duration=duration_days,
                dm_sent=dm_sent
            )
            
            # Update user trust score severely
            await self.update_trust_score(user_id, guild_id, -0.5)
            
            # If temporary ban, schedule unban task
            if duration_days:
                # In seconds
                unban_delay = duration_days * 24 * 60 * 60
                
                # Schedule the unban
                self.bot.loop.create_task(
                    self.schedule_unban(guild_id, user_id, moderator_id, unban_delay)
                )
            
        except Exception as e:
            logger.error(f"Error handling ban action: {str(e)}")
            db.session.rollback()
    
    async def schedule_unban(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        delay_seconds: int
    ):
        """
        Schedule an unban task for a temporary ban
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator (who issued the ban)
            delay_seconds: Delay in seconds before unbanning
        """
        await asyncio.sleep(delay_seconds)
        
        try:
            # Get guild
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id} for scheduled unban")
                return
                
            # Check if the ban is still active
            ban_record = db.session.query(ModerationAction).filter_by(
                guild_id=guild_id,
                user_id=user_id,
                action_type="ban",
                active=True
            ).order_by(ModerationAction.created_at.desc()).first()
            
            if not ban_record:
                logger.error(f"No active ban found for user {user_id} in guild {guild_id}")
                return
                
            # Check if the ban was manually lifted
            if not ban_record.active:
                logger.info(f"Ban for user {user_id} in guild {guild_id} already lifted manually")
                return
                
            # Unban the user
            try:
                await guild.unban(discord.Object(id=int(user_id)), reason="Temporary ban expired")
            except discord.NotFound:
                logger.warning(f"User {user_id} not found in guild {guild_id} ban list")
            except Exception as e:
                logger.error(f"Error unbanning user {user_id} in guild {guild_id}: {str(e)}")
                return
                
            # Update the ban record
            ban_record.active = False
            ban_record.updated_at = datetime.datetime.utcnow()
            db.session.commit()
            
            # Log the unban
            await self.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=str(self.bot.user.id),  # Bot is the moderator for automatic unbans
                action="unban",
                reason="Temporary ban expired"
            )
            
        except Exception as e:
            logger.error(f"Error in scheduled unban task: {str(e)}")
            db.session.rollback()
    
    async def handle_delete(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        message_id: str,
        reason: str,
        **kwargs
    ):
        """
        Handle message deletion action
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator
            message_id: The ID of the message to delete
            reason: The reason for the action
            **kwargs: Additional keyword arguments (includes channel_id)
        """
        try:
            # Get guild
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                return
                
            # Get channel
            channel_id = kwargs.get("channel_id")
            if not channel_id:
                logger.error("Channel ID required for message deletion")
                return
                
            channel = guild.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Could not find channel {channel_id} in guild {guild_id}")
                return
            
            # Delete the message
            try:
                message = await channel.fetch_message(int(message_id))
                await message.delete()
            except discord.NotFound:
                logger.warning(f"Message {message_id} not found in channel {channel_id}")
            except Exception as e:
                logger.error(f"Error deleting message {message_id}: {str(e)}")
                return
            
            # Record action in database
            delete_action = ModerationAction(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type="delete",
                message_id=message_id,
                channel_id=channel_id,
                reason=reason,
                active=False,  # Deletion is not an "active" state
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(delete_action)
            db.session.commit()
            
            # Log the action
            await self.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action="delete",
                reason=reason,
                channel_id=channel_id,
                message_id=message_id
            )
            
        except Exception as e:
            logger.error(f"Error handling delete action: {str(e)}")
            db.session.rollback()
    
    async def handle_timeout(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str,
        duration_minutes: int = 10,
        **kwargs
    ):
        """
        Handle timeout action (Discord's built-in timeout feature)
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator
            reason: The reason for the action
            duration_minutes: Duration of the timeout in minutes
            **kwargs: Additional keyword arguments
        """
        try:
            # Get guild and member
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                return
                
            member = guild.get_member(int(user_id))
            if not member:
                logger.error(f"Could not find member {user_id} in guild {guild_id}")
                return
            
            # Apply timeout
            await member.timeout(
                datetime.timedelta(minutes=duration_minutes),
                reason=reason
            )
            
            # Calculate end time
            end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration_minutes)
            
            # Record action in database
            timeout_action = ModerationAction(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type="timeout",
                reason=reason,
                expires_at=end_time,
                active=True,
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(timeout_action)
            db.session.commit()
            
            # Try to DM the user
            dm_sent = False
            try:
                # Create timeout embed
                embed = create_moderation_embed(
                    title="You Have Been Timed Out",
                    description=f"You have been timed out in **{guild.name}** for {duration_minutes} minutes",
                    moderator=guild.get_member(int(moderator_id)).display_name if guild.get_member(int(moderator_id)) else "System",
                    reason=reason,
                    color=0xFFA500,  # Orange color
                    include_timestamp=True
                )
                
                await member.send(embed=embed)
                dm_sent = True
            except Exception as e:
                logger.error(f"Error sending DM to timed out user: {str(e)}")
            
            # Log the action
            await self.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action="timeout",
                reason=reason,
                duration=duration_minutes,
                dm_sent=dm_sent
            )
            
            # Update user trust score
            await self.update_trust_score(user_id, guild_id, -0.05)
            
        except Exception as e:
            logger.error(f"Error handling timeout action: {str(e)}")
            db.session.rollback()
    
    async def log_moderation_action(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        action: str,
        reason: str,
        **kwargs
    ):
        """
        Log a moderation action to the configured log channel
        
        Args:
            guild_id: The Discord ID of the guild
            user_id: The Discord ID of the user
            moderator_id: The Discord ID of the moderator
            action: The type of action (warn, mute, kick, ban, etc.)
            reason: The reason for the action
            **kwargs: Additional information like channel_id, message_id, etc.
        """
        try:
            # Check if the guild has a configured mod log channel
            if guild_id not in self.mod_log_channels:
                return
                
            log_channel_id = self.mod_log_channels[guild_id]
            
            # Get channel
            channel = self.bot.get_channel(int(log_channel_id))
            if not channel:
                logger.error(f"Could not find mod log channel {log_channel_id} in guild {guild_id}")
                return
            
            # Get guild and users
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                logger.error(f"Could not find guild {guild_id}")
                return
                
            # Try to get member and moderator (they might not be in the guild)
            member = guild.get_member(int(user_id))
            moderator = guild.get_member(int(moderator_id))
            
            # Format user and moderator names
            user_name = member.display_name if member else f"Unknown ({user_id})"
            moderator_name = moderator.display_name if moderator else f"Unknown ({moderator_id})"
            
            # Action-specific colors
            colors = {
                "warning": 0xFFDD57,  # Yellow
                "mute": 0xFFA500,  # Orange
                "kick": 0xFF3860,  # Red
                "ban": 0x9D0000,  # Dark Red
                "unban": 0x00D26A,  # Green
                "delete": 0x3273DC,  # Blue
                "timeout": 0xFFA500,  # Orange
            }
            color = colors.get(action, 0x7289DA)  # Default Discord color
            
            # Format action name
            action_name = action.title()
            if action == "warning":
                level = kwargs.get("warning_level", "").title()
                if level:
                    action_name = f"{level} Warning"
            
            # Create embed for log channel
            embed = create_moderation_embed(
                title=f"{action_name} | {user_name}",
                description=f"**{action_name}** issued to {user_name}",
                user=user_name,
                user_id=user_id,
                moderator=moderator_name,
                reason=reason,
                dm_sent=kwargs.get("dm_sent"),
                color=color,
                include_timestamp=True
            )
            
            # Add duration if provided
            if "duration" in kwargs and kwargs["duration"]:
                if action in ["mute", "timeout"]:
                    duration_text = f"{kwargs['duration']} minutes"
                elif action == "ban":
                    duration_text = f"{kwargs['duration']} days" if kwargs["duration"] else "Permanent"
                embed.add_field(name="Duration", value=duration_text, inline=True)
            
            # Add channel info if provided
            if "channel_id" in kwargs and kwargs["channel_id"]:
                channel_mention = f"<#{kwargs['channel_id']}>"
                embed.add_field(name="Channel", value=channel_mention, inline=True)
            
            # Add message info if provided
            if "message_id" in kwargs and kwargs["message_id"]:
                embed.add_field(name="Message ID", value=kwargs["message_id"], inline=True)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging moderation action: {str(e)}")
    
    async def log_message_deletion(self, message: discord.Message):
        """
        Log a message deletion event
        
        Args:
            message: The Discord message that was deleted
        """
        try:
            guild_id = str(message.guild.id)
            
            # Check if the guild has a configured mod log channel
            if guild_id not in self.mod_log_channels:
                return
                
            log_channel_id = self.mod_log_channels[guild_id]
            
            # Get log channel
            channel = self.bot.get_channel(int(log_channel_id))
            if not channel:
                return
            
            # Create embed for the deleted message
            embed = discord.Embed(
                title="Message Deleted",
                description=f"Message by {message.author.mention} deleted in {message.channel.mention}",
                color=0x3273DC,  # Blue
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add message content if available
            if message.content:
                content = message.content
                if len(content) > 1024:
                    content = content[:1021] + "..."
                embed.add_field(name="Content", value=content, inline=False)
            
            # Add attachments info if any
            if message.attachments:
                attachments_text = "\n".join([f"{a.filename} ({a.size} bytes)" for a in message.attachments[:5]])
                if len(message.attachments) > 5:
                    attachments_text += f"\n... and {len(message.attachments) - 5} more"
                embed.add_field(name="Attachments", value=attachments_text, inline=False)
            
            # Add message details
            embed.add_field(name="Message ID", value=message.id, inline=True)
            embed.add_field(name="Author ID", value=message.author.id, inline=True)
            embed.add_field(name="Channel ID", value=message.channel.id, inline=True)
            
            # Set author information
            embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
            
            # Set footer
            embed.set_footer(text="Message Deletion Log")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging message deletion: {str(e)}")
    
    async def log_message_edit(self, before: discord.Message, after: discord.Message):
        """
        Log a message edit event
        
        Args:
            before: The Discord message before editing
            after: The Discord message after editing
        """
        try:
            guild_id = str(after.guild.id)
            
            # Check if the guild has a configured mod log channel
            if guild_id not in self.mod_log_channels:
                return
                
            log_channel_id = self.mod_log_channels[guild_id]
            
            # Get log channel
            channel = self.bot.get_channel(int(log_channel_id))
            if not channel:
                return
                
            # Ignore if content didn't change
            if before.content == after.content:
                return
            
            # Create embed for the edited message
            embed = discord.Embed(
                title="Message Edited",
                description=f"Message by {after.author.mention} edited in {after.channel.mention}",
                color=0x3273DC,  # Blue
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add before content
            before_content = before.content
            if len(before_content) > 1024:
                before_content = before_content[:1021] + "..."
            embed.add_field(name="Before", value=before_content or "No content", inline=False)
            
            # Add after content
            after_content = after.content
            if len(after_content) > 1024:
                after_content = after_content[:1021] + "..."
            embed.add_field(name="After", value=after_content or "No content", inline=False)
            
            # Add message details
            embed.add_field(name="Message ID", value=after.id, inline=True)
            embed.add_field(name="Author ID", value=after.author.id, inline=True)
            embed.add_field(name="Channel ID", value=after.channel.id, inline=True)
            
            # Add jump link
            embed.add_field(name="Jump to Message", value=f"[Click Here]({after.jump_url})", inline=False)
            
            # Set author information
            embed.set_author(name=str(after.author), icon_url=after.author.avatar_url)
            
            # Set footer
            embed.set_footer(text="Message Edit Log")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging message edit: {str(e)}")
    
    async def log_member_join(self, member: discord.Member):
        """
        Log a member join event
        
        Args:
            member: The Discord member who joined
        """
        try:
            guild_id = str(member.guild.id)
            
            # Check if the guild has a configured mod log channel
            if guild_id not in self.mod_log_channels:
                return
                
            log_channel_id = self.mod_log_channels[guild_id]
            
            # Get log channel
            channel = self.bot.get_channel(int(log_channel_id))
            if not channel:
                return
            
            # Calculate account age
            account_age = datetime.datetime.utcnow() - member.created_at
            account_age_str = f"{account_age.days} days"
            
            # Create embed for the member join
            embed = discord.Embed(
                title="Member Joined",
                description=f"{member.mention} joined the server",
                color=0x00D26A,  # Green
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add member details
            embed.add_field(name="Member ID", value=member.id, inline=True)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="Account Age", value=account_age_str, inline=True)
            
            # New account warning if account is less than 7 days old
            if account_age.days < 7:
                embed.add_field(
                    name="⚠️ New Account",
                    value=f"This account was created {account_age.days} days ago",
                    inline=False
                )
            
            # Set author information
            embed.set_author(name=str(member), icon_url=member.avatar_url)
            
            # Set footer
            embed.set_footer(text="Member Join Log")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging member join: {str(e)}")
    
    async def log_member_leave(self, member: discord.Member):
        """
        Log a member leave event
        
        Args:
            member: The Discord member who left
        """
        try:
            guild_id = str(member.guild.id)
            
            # Check if the guild has a configured mod log channel
            if guild_id not in self.mod_log_channels:
                return
                
            log_channel_id = self.mod_log_channels[guild_id]
            
            # Get log channel
            channel = self.bot.get_channel(int(log_channel_id))
            if not channel:
                return
            
            # Calculate time in server
            if member.joined_at:
                time_in_server = datetime.datetime.utcnow() - member.joined_at
                time_in_server_str = f"{time_in_server.days} days"
            else:
                time_in_server_str = "Unknown"
            
            # Check for active punishments
            active_punishments = db.session.query(ModerationAction).filter_by(
                guild_id=guild_id,
                user_id=str(member.id),
                active=True
            ).all()
            
            punishment_text = "None"
            if active_punishments:
                punishment_strs = []
                for punishment in active_punishments:
                    punishment_strs.append(f"{punishment.action_type.title()} ({punishment.created_at.strftime('%Y-%m-%d')})")
                punishment_text = ", ".join(punishment_strs)
            
            # Create embed for the member leave
            embed = discord.Embed(
                title="Member Left",
                description=f"{member.mention} left the server",
                color=0xFF3860,  # Red
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add member details
            embed.add_field(name="Member ID", value=member.id, inline=True)
            
            if member.joined_at:
                embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
                
            embed.add_field(name="Time in Server", value=time_in_server_str, inline=True)
            
            # Add roles if any
            if len(member.roles) > 1:  # Exclude @everyone
                role_str = ", ".join([role.name for role in member.roles[1:]])
                if len(role_str) > 1024:
                    role_str = role_str[:1021] + "..."
                embed.add_field(name="Roles", value=role_str, inline=False)
            
            # Add active punishments if any
            embed.add_field(name="Active Punishments", value=punishment_text, inline=False)
            
            # Set author information
            embed.set_author(name=str(member), icon_url=member.avatar_url)
            
            # Set footer
            embed.set_footer(text="Member Leave Log")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging member leave: {str(e)}")
    
    async def check_ban_evasion(self, member: discord.Member):
        """
        Check if a new member might be evading a ban
        
        Args:
            member: The Discord member who joined
        """
        try:
            guild_id = str(member.guild.id)
            user_id = str(member.id)
            
            # Get active bans for this guild
            active_bans = db.session.query(ModerationAction).filter_by(
                guild_id=guild_id,
                action_type="ban",
                active=True
            ).all()
            
            # No need to continue if there are no active bans
            if not active_bans:
                return
            
            # Check for suspicious patterns
            suspicious = False
            similar_to_banned = []
            
            # Check account age - very new accounts are suspicious
            account_age = datetime.datetime.utcnow() - member.created_at
            if account_age.days < 3:  # Less than 3 days old
                suspicious = True
            
            # More sophisticated ban evasion detection would go here
            
            # If suspicious, notify moderators
            if suspicious:
                # Log the suspicious join
                await self.log_suspicious_join(member)
                
                # Increase monitoring for this user
                await self.update_trust_score(user_id, guild_id, -0.2)  # Start with lower trust
                
        except Exception as e:
            logger.error(f"Error checking ban evasion: {str(e)}")
    
    async def log_suspicious_join(self, member: discord.Member):
        """
        Log a suspicious member join that might be ban evasion
        
        Args:
            member: The Discord member who joined
        """
        try:
            guild_id = str(member.guild.id)
            
            # Check if the guild has a configured mod log channel
            if guild_id not in self.mod_log_channels:
                return
                
            log_channel_id = self.mod_log_channels[guild_id]
            
            # Get log channel
            channel = self.bot.get_channel(int(log_channel_id))
            if not channel:
                return
            
            # Create embed for the suspicious join
            embed = discord.Embed(
                title="⚠️ Suspicious Account Join",
                description=f"{member.mention} joined the server and may be trying to evade a ban",
                color=0xFF3860,  # Red
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add member details
            embed.add_field(name="Member ID", value=member.id, inline=True)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            
            account_age = datetime.datetime.utcnow() - member.created_at
            embed.add_field(name="Account Age", value=f"{account_age.days} days", inline=True)
            
            # Set author information
            embed.set_author(name=str(member), icon_url=member.avatar_url)
            
            # Add recommendations
            embed.add_field(
                name="Recommended Actions",
                value="- Monitor this user closely\n- Check for similar behavior to banned users\n- Consider requiring verification",
                inline=False
            )
            
            # Set footer
            embed.set_footer(text="Potential Ban Evasion Alert")
            
            await channel.send(
                content="@here Potential ban evasion detected! Please review.",
                embed=embed
            )
            
        except Exception as e:
            logger.error(f"Error logging suspicious join: {str(e)}")

# Discord commands for moderation
class ModerationCommands(commands.Cog):
    def __init__(self, bot, moderation_service):
        self.bot = bot
        self.mod_service = moderation_service
    
    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn_command(self, ctx, member: discord.Member, level: str = "low", *, reason: str = "No reason provided"):
        """
        Warn a user
        
        Args:
            ctx: The command context
            member: The member to warn
            level: Warning level (low, medium, high, severe)
            reason: The reason for the warning
        """
        # Validate warning level
        valid_levels = ["low", "medium", "high", "severe"]
        if level.lower() not in valid_levels:
            await ctx.send(f"Invalid warning level. Valid levels are: {', '.join(valid_levels)}")
            return
        
        # Issue the warning
        await self.mod_service.issue_warning(
            user_id=str(member.id),
            guild_id=str(ctx.guild.id),
            moderator_id=str(ctx.author.id),
            reason=reason,
            warning_level=level.lower(),
            channel_id=str(ctx.channel.id)
        )
        
        # Respond to command
        embed = create_moderation_embed(
            title=f"{level.title()} Warning Issued",
            description=f"{member.mention} has been warned",
            user=str(member),
            user_id=str(member.id),
            moderator=ctx.author.display_name,
            reason=reason
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute_command(self, ctx, member: discord.Member, duration: int = 10, *, reason: str = "No reason provided"):
        """
        Mute a user
        
        Args:
            ctx: The command context
            member: The member to mute
            duration: Mute duration in minutes (default: 10)
            reason: The reason for the mute
        """
        # Check for valid duration
        if duration < 1:
            await ctx.send("Duration must be at least 1 minute")
            return
        
        # Issue the mute
        await self.mod_service.handle_mute(
            guild_id=str(ctx.guild.id),
            user_id=str(member.id),
            moderator_id=str(ctx.author.id),
            reason=reason,
            duration_minutes=duration
        )
        
        # Respond to command
        embed = create_moderation_embed(
            title="User Muted",
            description=f"{member.mention} has been muted for {duration} minutes",
            user=str(member),
            user_id=str(member.id),
            moderator=ctx.author.display_name,
            reason=reason
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_command(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """
        Kick a user from the server
        
        Args:
            ctx: The command context
            member: The member to kick
            reason: The reason for the kick
        """
        # Issue the kick
        await self.mod_service.handle_kick(
            guild_id=str(ctx.guild.id),
            user_id=str(member.id),
            moderator_id=str(ctx.author.id),
            reason=reason
        )
        
        # Respond to command
        embed = create_moderation_embed(
            title="User Kicked",
            description=f"{member.mention} has been kicked from the server",
            user=str(member),
            user_id=str(member.id),
            moderator=ctx.author.display_name,
            reason=reason
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_command(
        self, 
        ctx, 
        member: discord.Member, 
        duration: int = None, 
        delete_days: int = 1, 
        *, 
        reason: str = "No reason provided"
    ):
        """
        Ban a user from the server
        
        Args:
            ctx: The command context
            member: The member to ban
            duration: Ban duration in days (default: None, which means permanent)
            delete_days: Days of messages to delete (default: 1)
            reason: The reason for the ban
        """
        # Validate delete_days
        if delete_days < 0 or delete_days > 7:
            await ctx.send("delete_days must be between 0 and 7")
            return
        
        # Issue the ban
        await self.mod_service.handle_ban(
            guild_id=str(ctx.guild.id),
            user_id=str(member.id),
            moderator_id=str(ctx.author.id),
            reason=reason,
            duration_days=duration,
            delete_message_days=delete_days
        )
        
        # Format duration text
        duration_text = f" for {duration} days" if duration else " permanently"
        
        # Respond to command
        embed = create_moderation_embed(
            title="User Banned",
            description=f"{member.mention} has been banned{duration_text}",
            user=str(member),
            user_id=str(member.id),
            moderator=ctx.author.display_name,
            reason=reason
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_command(self, ctx, user_id: int, *, reason: str = "No reason provided"):
        """
        Unban a user from the server
        
        Args:
            ctx: The command context
            user_id: The ID of the user to unban
            reason: The reason for the unban
        """
        guild_id = str(ctx.guild.id)
        user_id_str = str(user_id)
        
        try:
            # Try to unban the user
            await ctx.guild.unban(discord.Object(id=user_id), reason=reason)
            
            # Update any active ban records
            ban_records = db.session.query(ModerationAction).filter_by(
                guild_id=guild_id,
                user_id=user_id_str,
                action_type="ban",
                active=True
            ).all()
            
            for record in ban_records:
                record.active = False
                record.updated_at = datetime.datetime.utcnow()
            
            db.session.commit()
            
            # Log the unban
            await self.mod_service.log_moderation_action(
                guild_id=guild_id,
                user_id=user_id_str,
                moderator_id=str(ctx.author.id),
                action="unban",
                reason=reason
            )
            
            # Try to get the username
            try:
                user = await self.bot.fetch_user(user_id)
                user_display = f"{user} ({user_id})"
            except:
                user_display = f"Unknown ({user_id})"
            
            # Respond to command
            embed = create_moderation_embed(
                title="User Unbanned",
                description=f"**{user_display}** has been unbanned",
                user=user_display,
                user_id=user_id_str,
                moderator=ctx.author.display_name,
                reason=reason,
                color=0x00D26A  # Green
            )
            
            await ctx.send(embed=embed)
            
        except discord.NotFound:
            await ctx.send(f"User with ID {user_id} not found in the ban list")
        except Exception as e:
            logger.error(f"Error unbanning user: {str(e)}")
            await ctx.send(f"Error unbanning user: {str(e)}")
            db.session.rollback()
    
    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge_command(self, ctx, amount: int, user: discord.Member = None):
        """
        Purge messages from a channel
        
        Args:
            ctx: The command context
            amount: Number of messages to purge (1-100)
            user: Optional user to filter messages by
        """
        # Validate amount
        if amount < 1 or amount > 100:
            await ctx.send("Amount must be between 1 and 100")
            return
        
        # Purge messages
        try:
            # Check if filtering by user
            if user:
                def check(message):
                    return message.author.id == user.id
                
                deleted = await ctx.channel.purge(limit=amount, check=check)
                
                # Log the purge
                await self.mod_service.log_moderation_action(
                    guild_id=str(ctx.guild.id),
                    user_id=str(user.id),
                    moderator_id=str(ctx.author.id),
                    action="purge",
                    reason=f"Purged {len(deleted)} messages from {user}",
                    channel_id=str(ctx.channel.id)
                )
                
                # Respond to command
                embed = create_moderation_embed(
                    title="Messages Purged",
                    description=f"Purged {len(deleted)} messages from {user.mention} in {ctx.channel.mention}",
                    moderator=ctx.author.display_name,
                    color=0x3273DC  # Blue
                )
                
            else:
                deleted = await ctx.channel.purge(limit=amount)
                
                # Log the purge
                await self.mod_service.log_moderation_action(
                    guild_id=str(ctx.guild.id),
                    user_id="0",  # No specific user
                    moderator_id=str(ctx.author.id),
                    action="purge",
                    reason=f"Purged {len(deleted)} messages",
                    channel_id=str(ctx.channel.id)
                )
                
                # Respond to command
                embed = create_moderation_embed(
                    title="Messages Purged",
                    description=f"Purged {len(deleted)} messages in {ctx.channel.mention}",
                    moderator=ctx.author.display_name,
                    color=0x3273DC  # Blue
                )
            
            # Send response that auto-deletes after 5 seconds
            response = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await response.delete()
            
        except Exception as e:
            logger.error(f"Error purging messages: {str(e)}")
            await ctx.send(f"Error purging messages: {str(e)}")
    
    @commands.command(name="modlog")
    @commands.has_permissions(administrator=True)
    async def modlog_command(self, ctx, channel: discord.TextChannel = None):
        """
        Set or view the moderation log channel
        
        Args:
            ctx: The command context
            channel: The channel to set as the mod log (or None to view current)
        """
        guild_id = str(ctx.guild.id)
        
        if channel:
            # Set the mod log channel
            try:
                # Check if a log channel already exists
                existing_log = db.session.query(ModLog).filter_by(guild_id=guild_id).first()
                
                if existing_log:
                    # Update existing record
                    existing_log.channel_id = str(channel.id)
                    existing_log.updated_at = datetime.datetime.utcnow()
                else:
                    # Create new record
                    new_log = ModLog(
                        guild_id=guild_id,
                        channel_id=str(channel.id),
                        created_at=datetime.datetime.utcnow()
                    )
                    db.session.add(new_log)
                
                db.session.commit()
                
                # Update the cached value
                self.mod_service.mod_log_channels[guild_id] = str(channel.id)
                
                # Respond to command
                await ctx.send(f"✅ Moderation logs will now be sent to {channel.mention}")
                
            except Exception as e:
                logger.error(f"Error setting mod log channel: {str(e)}")
                await ctx.send(f"Error setting mod log channel: {str(e)}")
                db.session.rollback()
        else:
            # View the current mod log channel
            if guild_id in self.mod_service.mod_log_channels:
                channel_id = self.mod_service.mod_log_channels[guild_id]
                channel = ctx.guild.get_channel(int(channel_id))
                
                if channel:
                    await ctx.send(f"Current moderation log channel: {channel.mention}")
                else:
                    await ctx.send("Moderation log channel is set but could not be found")
            else:
                await ctx.send("No moderation log channel set. Use `!modlog #channel` to set one")
    
    @commands.group(name="automod", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def automod_command(self, ctx):
        """Base command for auto-moderation settings"""
        await ctx.send("Please specify an automod subcommand. Use `!help automod` for more information")
    
    @automod_command.command(name="status")
    async def automod_status(self, ctx):
        """Show auto-moderation status"""
        guild_id = str(ctx.guild.id)
        
        try:
            # Get all auto-mod rules for this guild
            rules = db.session.query(AutoModRule).filter_by(guild_id=guild_id).all()
            
            if not rules:
                await ctx.send("No auto-moderation rules configured for this server")
                return
                
            # Create embed
            embed = discord.Embed(
                title="Auto-Moderation Status",
                description=f"This server has {len(rules)} auto-mod rules configured",
                color=0x3273DC,  # Blue
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add rules to embed
            for rule in rules:
                status = "✅ Enabled" if rule.enabled else "❌ Disabled"
                embed.add_field(
                    name=f"{rule.name} ({status})",
                    value=f"Type: {rule.rule_type}\nPriority: {rule.priority}",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting automod status: {str(e)}")
            await ctx.send(f"Error getting automod status: {str(e)}")
    
    @automod_command.command(name="add")
    async def automod_add(self, ctx, name: str, rule_type: str, *, settings: str):
        """
        Add an auto-moderation rule
        
        Args:
            ctx: The command context
            name: Name for the rule
            rule_type: Type of rule (regex, word_filter, link_filter, etc.)
            settings: JSON settings for the rule
        """
        guild_id = str(ctx.guild.id)
        
        # Validate rule type
        valid_types = [
            "regex", "word_filter", "link_filter", "spam_detection",
            "mention_limit", "attachment_filter", "ai_toxic_content"
        ]
        
        if rule_type.lower() not in valid_types:
            await ctx.send(f"Invalid rule type. Valid types are: {', '.join(valid_types)}")
            return
        
        # Validate settings JSON
        try:
            settings_dict = json.loads(settings)
        except json.JSONDecodeError:
            await ctx.send("Invalid settings JSON. Please provide valid JSON")
            return
        
        try:
            # Get the highest priority rule
            highest_priority = db.session.query(func.max(AutoModRule.priority)).filter_by(guild_id=guild_id).scalar() or 0
            
            # Create new rule
            new_rule = AutoModRule(
                guild_id=guild_id,
                name=name,
                rule_type=rule_type.lower(),
                rule_settings=settings,
                priority=highest_priority + 1,
                enabled=True,
                created_by=str(ctx.author.id),
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(new_rule)
            db.session.commit()
            
            # Respond to command
            await ctx.send(f"✅ Auto-moderation rule '{name}' added successfully with priority {highest_priority + 1}")
            
        except Exception as e:
            logger.error(f"Error adding automod rule: {str(e)}")
            await ctx.send(f"Error adding automod rule: {str(e)}")
            db.session.rollback()
    
    @automod_command.command(name="remove")
    async def automod_remove(self, ctx, rule_id: int):
        """
        Remove an auto-moderation rule
        
        Args:
            ctx: The command context
            rule_id: ID of the rule to remove
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Get the rule
            rule = db.session.query(AutoModRule).filter_by(
                id=rule_id,
                guild_id=guild_id
            ).first()
            
            if not rule:
                await ctx.send(f"Rule with ID {rule_id} not found")
                return
                
            # Delete the rule
            db.session.delete(rule)
            db.session.commit()
            
            # Respond to command
            await ctx.send(f"✅ Auto-moderation rule '{rule.name}' removed successfully")
            
        except Exception as e:
            logger.error(f"Error removing automod rule: {str(e)}")
            await ctx.send(f"Error removing automod rule: {str(e)}")
            db.session.rollback()
    
    @automod_command.command(name="enable")
    async def automod_enable(self, ctx, rule_id: int):
        """
        Enable an auto-moderation rule
        
        Args:
            ctx: The command context
            rule_id: ID of the rule to enable
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Get the rule
            rule = db.session.query(AutoModRule).filter_by(
                id=rule_id,
                guild_id=guild_id
            ).first()
            
            if not rule:
                await ctx.send(f"Rule with ID {rule_id} not found")
                return
                
            # Enable the rule
            rule.enabled = True
            rule.updated_at = datetime.datetime.utcnow()
            db.session.commit()
            
            # Respond to command
            await ctx.send(f"✅ Auto-moderation rule '{rule.name}' enabled successfully")
            
        except Exception as e:
            logger.error(f"Error enabling automod rule: {str(e)}")
            await ctx.send(f"Error enabling automod rule: {str(e)}")
            db.session.rollback()
    
    @automod_command.command(name="disable")
    async def automod_disable(self, ctx, rule_id: int):
        """
        Disable an auto-moderation rule
        
        Args:
            ctx: The command context
            rule_id: ID of the rule to disable
        """
        guild_id = str(ctx.guild.id)
        
        try:
            # Get the rule
            rule = db.session.query(AutoModRule).filter_by(
                id=rule_id,
                guild_id=guild_id
            ).first()
            
            if not rule:
                await ctx.send(f"Rule with ID {rule_id} not found")
                return
                
            # Disable the rule
            rule.enabled = False
            rule.updated_at = datetime.datetime.utcnow()
            db.session.commit()
            
            # Respond to command
            await ctx.send(f"✅ Auto-moderation rule '{rule.name}' disabled successfully")
            
        except Exception as e:
            logger.error(f"Error disabling automod rule: {str(e)}")
            await ctx.send(f"Error disabling automod rule: {str(e)}")
            db.session.rollback()
    
    @commands.command(name="trust")
    @commands.has_permissions(manage_guild=True)
    async def trust_command(self, ctx, member: discord.Member):
        """
        Check a user's trust score
        
        Args:
            ctx: The command context
            member: The member to check
        """
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        try:
            # Get trust score
            trust_score = await self.mod_service.get_user_trust_score(user_id, guild_id)
            trust_percent = round(trust_score * 100, 1)
            
            # Determine trust level description
            if trust_score >= 0.8:
                trust_level = "Very High"
                color = 0x00D26A  # Green
            elif trust_score >= 0.6:
                trust_level = "High"
                color = 0x7CFC00  # Lawn Green
            elif trust_score >= 0.4:
                trust_level = "Medium"
                color = 0xFFDD57  # Yellow
            elif trust_score >= 0.2:
                trust_level = "Low"
                color = 0xFFA500  # Orange
            else:
                trust_level = "Very Low"
                color = 0xFF3860  # Red
            
            # Create embed
            embed = discord.Embed(
                title=f"Trust Score: {trust_level}",
                description=f"{member.mention} has a trust score of **{trust_percent}%**",
                color=color,
                timestamp=datetime.datetime.utcnow()
            )
            
            # Add user information
            embed.add_field(name="User ID", value=member.id, inline=True)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
            
            if member.joined_at:
                embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
            
            # Add warning count
            warnings = db.session.query(ModerationAction).filter_by(
                guild_id=guild_id,
                user_id=user_id,
                action_type="warning"
            ).count()
            
            embed.add_field(name="Warnings", value=warnings, inline=True)
            
            # Add moderation action count
            actions = db.session.query(ModerationAction).filter_by(
                guild_id=guild_id,
                user_id=user_id
            ).count()
            
            embed.add_field(name="Total Mod Actions", value=actions, inline=True)
            
            # Add auto-mod triggers
            triggers = db.session.query(func.count(ModTrigger.id)).filter_by(
                guild_id=guild_id,
                user_id=user_id
            ).scalar() or 0
            
            triggers += db.session.query(func.count(AutoModTrigger.id)).filter_by(
                guild_id=guild_id,
                user_id=user_id
            ).scalar() or 0
            
            embed.add_field(name="Auto-Mod Triggers", value=triggers, inline=True)
            
            # Set author information
            embed.set_author(name=str(member), icon_url=member.avatar_url)
            
            # Set footer
            embed.set_footer(text="Trust Score | AstroBot Enhanced Moderation")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting trust score: {str(e)}")
            await ctx.send(f"Error getting trust score: {str(e)}")

def setup(bot):
    # Create and initialize the moderation service
    mod_service = AdvancedModerationSystem(bot)
    bot.loop.create_task(mod_service.initialize())
    
    # Register the commands
    bot.add_cog(ModerationCommands(bot, mod_service))
    
    # Make the service available to other cogs
    bot.mod_service = mod_service