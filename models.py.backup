from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, Float, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import json

from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON

class User(db.Model):
    """User model for both Discord users and Twitch streamers"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(20), unique=True, nullable=False, index=True)
    discord_username = Column(String(100), nullable=False)
    discord_avatar = Column(String(255), nullable=True)
    twitch_id = Column(String(20), unique=True, nullable=True, index=True)
    twitch_username = Column(String(100), nullable=True)
    twitch_avatar = Column(String(255), nullable=True)
    points = Column(Integer, default=0, nullable=False)
    is_streamer = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_moderator = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    servers = relationship("MinecraftServer", back_populates="owner")
    reviews = relationship("ModReview", back_populates="user")
    suggestions = relationship("ModSuggestion", back_populates="user")
    point_transactions = relationship("PointTransaction", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.discord_username}>"

class MinecraftServer(db.Model):
    """Minecraft server model"""
    __tablename__ = 'minecraft_servers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=25565, nullable=False)
    rcon_port = Column(Integer, default=25575, nullable=True)
    rcon_password = Column(String(100), nullable=True)
    version = Column(String(20), nullable=True)
    server_type = Column(String(20), nullable=True) # vanilla, paper, spigot, forge, fabric
    auto_start = Column(Boolean, default=False)
    memory_allocation = Column(Integer, default=2048) # MB
    status = Column(String(20), default="offline") # online, offline, restarting
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="servers")
    whitelist = relationship("WhitelistEntry", back_populates="server")
    
    def __repr__(self):
        return f"<MinecraftServer {self.name}>"
        
class WhitelistEntry(db.Model):
    """Minecraft server whitelist entry"""
    __tablename__ = 'whitelist_entries'
    
    id = Column(Integer, primary_key=True)
    minecraft_username = Column(String(100), nullable=False)
    minecraft_uuid = Column(String(36), nullable=True)
    server_id = Column(Integer, ForeignKey('minecraft_servers.id'))
    added_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    server = relationship("MinecraftServer", back_populates="whitelist")
    
    def __repr__(self):
        return f"<WhitelistEntry {self.minecraft_username}>"

class ModReview(db.Model):
    """Minecraft mod review"""
    __tablename__ = 'mod_reviews'
    
    id = Column(Integer, primary_key=True)
    mod_name = Column(String(100), nullable=False, index=True)
    rating = Column(Integer, nullable=False) # 1-5
    review_text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<ModReview {self.mod_name} - {self.rating}/5>"

class ModSuggestion(db.Model):
    """Minecraft mod suggestion"""
    __tablename__ = 'mod_suggestions'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    ai_feedback = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="suggestions")
    
    def __repr__(self):
        return f"<ModSuggestion {self.title}>"

class BotSetting(db.Model):
    """Discord bot settings"""
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<BotSetting {self.key}>"
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        setting = cls.query.filter_by(key=key).first()
        if setting and setting.value:
            return setting.value
        return default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """Set a setting value"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

class CommandUsage(db.Model):
    """Discord command usage tracking"""
    __tablename__ = 'command_usage'
    
    id = Column(Integer, primary_key=True)
    command_name = Column(String(100), nullable=False, index=True)
    command_category = Column(String(50), nullable=True)
    discord_id = Column(String(20), nullable=True, index=True)
    discord_username = Column(String(100), nullable=True)
    guild_id = Column(String(20), nullable=True, index=True)
    channel_id = Column(String(20), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<CommandUsage {self.command_name}>"

class CustomCommand(db.Model):
    """Custom Discord commands"""
    __tablename__ = 'custom_commands'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    response_type = Column(String(20), default="text") # text, embed, javascript
    response_data = Column(Text, nullable=False)
    category = Column(String(50), default="custom")
    cooldown = Column(Integer, default=0) # seconds
    permissions = Column(String(20), default="everyone") # everyone, moderator, admin, owner
    enabled = Column(Boolean, default=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<CustomCommand {self.name}>"
    
    def get_response_data(self):
        """Get response data as dictionary"""
        if self.response_type == "embed":
            try:
                return json.loads(self.response_data)
            except:
                return {"title": "Error", "description": "Invalid embed data"}
        return self.response_data

class PointTransaction(db.Model):
    """Community points transaction tracking"""
    __tablename__ = 'point_transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    source = Column(String(50), nullable=False) # discord, twitch, minecraft, admin
    source_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="point_transactions")
    
    def __repr__(self):
        return f"<PointTransaction {self.amount} points for {self.user_id}>"

class WebsiteUser(UserMixin, db.Model):
    """User model for website login"""
    __tablename__ = 'website_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    discord_id = Column(String(20), unique=True, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")
    
    def __repr__(self):
        return f"<WebsiteUser {self.username}>"
    
    def set_password(self, password):
        """Set user password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)


class Feedback(db.Model):
    """User feedback and suggestions"""
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True)
    feedback_type = Column(String(20), nullable=False) # bug_report, feature_request, improvement, general_feedback, question
    feature_category = Column(String(20), nullable=True) # moderation, custom_commands, minecraft, twitch, ai, music, web_dashboard, api, other
    subject = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    contact_info = Column(String(100), nullable=True)
    can_contact = Column(Boolean, default=False)
    status = Column(String(20), default="pending") # pending, reviewing, implemented, rejected, closed
    user_id = Column(Integer, ForeignKey('website_users.id'), nullable=True)
    discord_id = Column(String(20), nullable=True)
    discord_username = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("WebsiteUser", back_populates="feedback")
    
    def __repr__(self):
        return f"<Feedback {self.id} - {self.subject}>"


class DocumentationFeedback(db.Model):
    """Feedback on documentation pages"""
    __tablename__ = 'documentation_feedback'
    
    id = Column(Integer, primary_key=True)
    page_path = Column(String(255), nullable=False)
    helpful = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('website_users.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentationFeedback {self.id} - {self.helpful}>"


class ApiKey(db.Model):
    """API key for external access"""
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    permissions = Column(String(20), default="read") # read, write, admin
    user_id = Column(Integer, ForeignKey('website_users.id'), nullable=False)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("WebsiteUser", back_populates="api_keys")
    
    def __repr__(self):
        return f"<ApiKey {self.id} - {self.permissions}>"


class Webhook(db.Model):
    """External webhook configuration"""
    __tablename__ = 'webhooks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    url = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False) # all, moderation, user_join_leave, message, command
    guild_id = Column(String(20), nullable=True)
    active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey('website_users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Webhook {self.name} - {self.event_type}>"


class AIUsage(db.Model):
    """AI usage tracking"""
    __tablename__ = 'ai_usage'
    
    id = Column(Integer, primary_key=True)
    model = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    feature = Column(String(50), nullable=True) # ask, fix, idea, tutorial, generate, code
    discord_id = Column(String(20), nullable=True, index=True)
    successful = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<AIUsage {self.model} - {self.total_tokens} tokens>"

class TwitchStream(db.Model):
    """Twitch stream tracking"""
    __tablename__ = 'twitch_streams'
    
    id = Column(Integer, primary_key=True)
    twitch_id = Column(String(20), nullable=False, index=True)
    twitch_username = Column(String(100), nullable=False)
    title = Column(String(255), nullable=True)
    game_name = Column(String(100), nullable=True)
    viewer_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    is_live = Column(Boolean, default=False)
    thumbnail_url = Column(String(255), nullable=True)
    discord_message_id = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<TwitchStream {self.twitch_username}>"

class StreamNotification(db.Model):
    """Twitch stream notification tracking"""
    __tablename__ = 'stream_notifications'
    
    id = Column(Integer, primary_key=True)
    twitch_id = Column(String(20), nullable=False, index=True)
    twitch_username = Column(String(100), nullable=False)
    notification_type = Column(String(50), nullable=False) # live, offline, milestone
    guild_id = Column(String(20), nullable=True, index=True)
    channel_id = Column(String(20), nullable=True)
    message_id = Column(String(20), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<StreamNotification {self.twitch_username} - {self.notification_type}>"

class ModerationAction(db.Model):
    """Discord moderation action tracking"""
    __tablename__ = 'moderation_actions'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False, index=True)
    user_id = Column(String(20), nullable=False, index=True)
    moderator_id = Column(String(20), nullable=False, index=True)
    action_type = Column(String(20), nullable=False) # warning, mute, unmute, ban, unban, kick
    reason = Column(Text, nullable=True)
    active = Column(Boolean, default=False) # For mutes and bans
    duration_minutes = Column(Integer, nullable=True) # For temporary mutes
    expiry_time = Column(DateTime, nullable=True) # For temporary mutes
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<ModerationAction {self.action_type} for {self.user_id}>"

class AutoModRule(db.Model):
    """Discord auto-moderation rule configuration"""
    __tablename__ = 'automod_rules'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    rule_type = Column(String(50), nullable=False) # spam, offensive_language, mention_spam, link_filtering
    enabled = Column(Boolean, default=True)
    action = Column(String(50), nullable=False) # delete, mute, warn, notify
    action_duration_minutes = Column(Integer, nullable=True) # For temporary mutes
    notify_channel_id = Column(String(20), nullable=True) # For notifications
    created_by = Column(String(20), nullable=True)
    settings = Column(JSON, nullable=True) # JSON configuration for the rule
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<AutoModRule {self.name} for {self.guild_id}>"

class AutoModTrigger(db.Model):
    """Record of auto-moderation rule being triggered"""
    __tablename__ = 'automod_triggers'
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('automod_rules.id'))
    guild_id = Column(String(20), nullable=False, index=True)
    user_id = Column(String(20), nullable=False, index=True)
    channel_id = Column(String(20), nullable=True)
    message_id = Column(String(20), nullable=True)
    trigger_type = Column(String(50), nullable=False)
    content_snippet = Column(String(255), nullable=True) # Snippet of the triggering content
    action_taken = Column(String(50), nullable=False) # delete, mute, warn, notify
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    rule = relationship("AutoModRule")
    
    def __repr__(self):
        return f"<AutoModTrigger rule_id={self.rule_id} user_id={self.user_id}>"

class WebhookIntegration(db.Model):
    """External service webhook integration"""
    __tablename__ = 'webhook_integrations'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(String(20), nullable=False, index=True)
    channel_id = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    service = Column(String(50), nullable=False) # github, trello, gitlab, jenkins, custom
    enabled = Column(Boolean, default=True)
    secret = Column(String(255), nullable=True) # For webhook verification
    token = Column(String(255), nullable=True) # For API authentication
    settings = Column(Text, nullable=True) # JSON settings for the integration
    endpoint_path = Column(String(100), nullable=True) # Custom endpoint path
    created_by = Column(String(20), nullable=True) # Discord ID of user who created the integration
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    events = relationship("WebhookEvent", back_populates="integration")
    
    def __repr__(self):
        return f"<WebhookIntegration {self.name} for {self.guild_id}>"
    
    def get_settings(self):
        """Get settings as dictionary"""
        if self.settings:
            try:
                return json.loads(self.settings)
            except:
                return {}
        return {}

class WebhookEvent(db.Model):
    """Record of webhook event"""
    __tablename__ = 'webhook_events'
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey('webhook_integrations.id'))
    event_type = Column(String(50), nullable=False, index=True)
    payload = Column(Text, nullable=True) # JSON payload
    processed = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    integration = relationship("WebhookIntegration", back_populates="events")
    
    def __repr__(self):
        return f"<WebhookEvent {self.event_type} for integration_id={self.integration_id}>"
    
    def get_payload(self):
        """Get payload as dictionary"""
        if self.payload:
            try:
                return json.loads(self.payload)
            except:
                return {}
        return {}