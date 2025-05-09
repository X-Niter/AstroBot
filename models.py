from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, Float, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime
import json

from app import db

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