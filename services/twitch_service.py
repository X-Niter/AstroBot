import os
import logging
import aiohttp
from datetime import datetime, timedelta

from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET
from services.mongo_service import update_user_points, get_user_by_twitch_id

# Configure logging
logger = logging.getLogger(__name__)

# Cache for access token
_access_token = None
_token_expiry = None

async def _get_access_token():
    """
    Get a Twitch API access token
    
    Returns:
        str: Access token
    """
    global _access_token, _token_expiry
    
    # If we have a valid token, return it
    now = datetime.now()
    if _access_token and _token_expiry and _token_expiry > now:
        return _access_token
    
    # Otherwise, get a new token
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://id.twitch.tv/oauth2/token"
            params = {
                "client_id": TWITCH_CLIENT_ID,
                "client_secret": TWITCH_CLIENT_SECRET,
                "grant_type": "client_credentials"
            }
            
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    _access_token = data["access_token"]
                    _token_expiry = now + timedelta(seconds=data["expires_in"] - 100)  # Buffer of 100 seconds
                    return _access_token
                else:
                    logger.error(f"Failed to get Twitch access token: {response.status}")
                    raise Exception(f"Failed to get Twitch access token: {response.status}")
    except Exception as e:
        logger.error(f"Error getting Twitch access token: {str(e)}")
        raise

async def get_user_info(username):
    """
    Get information about a Twitch user
    
    Args:
        username (str): Twitch username
        
    Returns:
        dict: User information
    """
    try:
        access_token = await _get_access_token()
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.twitch.tv/helix/users"
            headers = {
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {access_token}"
            }
            params = {"login": username}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["data"] and len(data["data"]) > 0:
                        return {
                            "id": data["data"][0]["id"],
                            "login": data["data"][0]["login"],
                            "display_name": data["data"][0]["display_name"],
                            "profile_image_url": data["data"][0]["profile_image_url"],
                            "description": data["data"][0]["description"]
                        }
                    else:
                        return None
                else:
                    logger.error(f"Failed to get Twitch user info: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error getting Twitch user info: {str(e)}")
        raise

async def get_stream_info(username):
    """
    Get information about a Twitch stream
    
    Args:
        username (str): Twitch username
        
    Returns:
        dict: Stream information
    """
    try:
        access_token = await _get_access_token()
        
        # Get user info first to get the user ID
        user_info = await get_user_info(username)
        if not user_info:
            return {
                "is_live": False,
                "profile_image_url": None
            }
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.twitch.tv/helix/streams"
            headers = {
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {access_token}"
            }
            params = {"user_id": user_info["id"]}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["data"] and len(data["data"]) > 0:
                        stream = data["data"][0]
                        
                        # Convert started_at to a relative time
                        started_at = datetime.fromisoformat(stream["started_at"].replace('Z', '+00:00'))
                        now = datetime.now(started_at.tzinfo)
                        duration = now - started_at
                        
                        if duration.total_seconds() < 3600:
                            started_at_str = f"{int(duration.total_seconds() / 60)} minutes ago"
                        else:
                            hours = int(duration.total_seconds() / 3600)
                            started_at_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
                        
                        return {
                            "is_live": True,
                            "title": stream["title"],
                            "game": stream["game_name"],
                            "viewers": stream["viewer_count"],
                            "started_at": started_at_str,
                            "thumbnail_url": stream["thumbnail_url"],
                            "profile_image_url": user_info["profile_image_url"]
                        }
                    else:
                        return {
                            "is_live": False,
                            "profile_image_url": user_info["profile_image_url"]
                        }
                else:
                    logger.error(f"Failed to get Twitch stream info: {response.status}")
                    return {
                        "is_live": False,
                        "profile_image_url": user_info["profile_image_url"]
                    }
    except Exception as e:
        logger.error(f"Error getting Twitch stream info: {str(e)}")
        raise

async def get_clips(username, limit=3):
    """
    Get recent clips from a Twitch channel
    
    Args:
        username (str): Twitch username
        limit (int): Number of clips to fetch
        
    Returns:
        list: List of clips
    """
    try:
        access_token = await _get_access_token()
        
        # Get user info first to get the user ID
        user_info = await get_user_info(username)
        if not user_info:
            return []
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.twitch.tv/helix/clips"
            headers = {
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {access_token}"
            }
            params = {
                "broadcaster_id": user_info["id"],
                "first": limit
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["data"] and len(data["data"]) > 0:
                        return [{
                            "id": clip["id"],
                            "title": clip["title"],
                            "url": clip["url"],
                            "view_count": clip["view_count"],
                            "created_at": clip["created_at"]
                        } for clip in data["data"]]
                    else:
                        return []
                else:
                    logger.error(f"Failed to get Twitch clips: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error getting Twitch clips: {str(e)}")
        raise

async def award_points(discord_id, points, reason, awarded_by):
    """
    Award support points to a user
    
    Args:
        discord_id (str): Discord user ID
        points (int): Number of points to award
        reason (str): Reason for awarding points
        awarded_by (str): Discord user ID of the person awarding the points
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Update user points in MongoDB
        result = await update_user_points(
            discord_id=discord_id,
            points_to_add=points,
            reason=reason,
            awarded_by=awarded_by
        )
        
        return result
    except Exception as e:
        logger.error(f"Error awarding points: {str(e)}")
        raise
