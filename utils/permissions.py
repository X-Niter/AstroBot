import discord
import logging

logger = logging.getLogger(__name__)

# Admin role name (customize as needed)
ADMIN_ROLE_NAME = "Admin"
MODERATOR_ROLE_NAMES = ["Moderator", "Mod"]

async def is_admin(user):
    """
    Check if a user has administrator permissions
    
    Args:
        user (discord.Member): The user to check
        
    Returns:
        bool: True if the user is an admin, False otherwise
    """
    if not hasattr(user, "guild_permissions"):
        return False
    
    # Check if user has administrator permission
    if user.guild_permissions.administrator:
        return True
    
    # Check if user has admin role
    return any(role.name == ADMIN_ROLE_NAME for role in user.roles)

async def is_moderator(user):
    """
    Check if a user has moderator permissions
    
    Args:
        user (discord.Member): The user to check
        
    Returns:
        bool: True if the user is a moderator, False otherwise
    """
    if not hasattr(user, "guild_permissions"):
        return False
    
    # Admin is also a moderator
    if await is_admin(user):
        return True
    
    # Check if user has any moderator role
    return any(role.name in MODERATOR_ROLE_NAMES for role in user.roles)

async def check_user_permissions(user, required_permission):
    """
    Check if a user has a specific permission
    
    Args:
        user (discord.Member): The user to check
        required_permission (str): The permission to check for
        
    Returns:
        bool: True if the user has the permission, False otherwise
    """
    if not hasattr(user, "guild_permissions"):
        return False
    
    # Check if user is an admin (admins have all permissions)
    if await is_admin(user):
        return True
    
    # Check for specific permission
    return getattr(user.guild_permissions, required_permission, False)
