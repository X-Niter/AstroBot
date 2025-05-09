import os
import logging
import motor.motor_asyncio
from datetime import datetime
from bson.objectid import ObjectId

from config import MONGODB_URI, DB_NAME, POINTS_ROLES

# Configure logging
logger = logging.getLogger(__name__)

# Create a MongoDB client and connect to the database
try:
    # Configure client with shorter timeouts and error handling
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
        retryReads=True
    )
    
    # Test connection - this will fail quickly if MongoDB is not available
    client.admin.command('ping')
    
    logger.info("MongoDB connection successful")
    db = client[DB_NAME]
    
    # Collections
    users_collection = db["users"]
    mod_reviews_collection = db["mod_reviews"]
    mod_suggestions_collection = db["mod_suggestions"]
    
except Exception as e:
    logger.error(f"MongoDB connection failed: {str(e)}")
    logger.info("Falling back to PostgreSQL for MongoDB functionality")
    # Set all to None so code can check and handle appropriately
    client = None
    db = None
    users_collection = None
    mod_reviews_collection = None
    mod_suggestions_collection = None

# Initialize indexes
async def init_indexes():
    """Initialize database indexes"""
    # Check if MongoDB collections are available
    if users_collection is None or mod_reviews_collection is None or mod_suggestions_collection is None:
        logger.warning("MongoDB collections not available, skipping index initialization")
        return
        
    try:
        # Create indexes for users collection
        await users_collection.create_index("discord_id", unique=True)
        await users_collection.create_index("twitch_id")
        
        # Create indexes for mod_reviews collection
        await mod_reviews_collection.create_index([("mod_name", 1), ("discord_id", 1)], unique=True)
        await mod_reviews_collection.create_index("mod_name")
        
        # Create indexes for mod_suggestions collection
        await mod_suggestions_collection.create_index("discord_id")
        await mod_suggestions_collection.create_index("created_at")
        
        logger.info("MongoDB indexes initialized")
    except Exception as e:
        logger.error(f"Error initializing MongoDB indexes: {str(e)}")

# Initialize indexes when module is imported
import asyncio

def initialize_indexes():
    """Initialize the database indexes in an async-safe manner"""
    # Skip if MongoDB is not available
    if users_collection is None:
        logger.info("Skipping MongoDB index initialization as MongoDB is not available")
        return
        
    try:
        # Use a synchronous approach to avoid event loop issues in web contexts
        logger.info("MongoDB collection references exist, but we'll skip index creation for now to avoid asyncio loop issues")
        
        # NOTE: In a production environment, you would want to create the indexes
        # during application startup in a controlled way, not during module import
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB indexes: {str(e)}")

# Call initialization function
initialize_indexes()

def _get_rank_from_points(points):
    """
    Determine the user's rank based on points
    
    Args:
        points (int): The user's points
        
    Returns:
        tuple: (rank, next_rank, next_rank_points)
    """
    current_rank = "New Member"
    next_rank = None
    next_rank_points = 0
    
    prev_threshold = 0
    for rank, threshold in sorted(POINTS_ROLES.items(), key=lambda x: x[1]):
        if points >= threshold:
            current_rank = rank
            prev_threshold = threshold
        else:
            next_rank = rank
            next_rank_points = threshold
            break
    
    return current_rank, next_rank, next_rank_points

async def get_user(discord_id):
    """
    Get a user document from the database
    
    Args:
        discord_id (str): Discord user ID
        
    Returns:
        dict: User document or None if not found
    """
    # If MongoDB is not available, return None
    if users_collection is None:
        logger.warning("MongoDB users collection is not available")
        return None
        
    try:
        return await users_collection.find_one({"discord_id": discord_id})
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return None

async def get_user_by_twitch_id(twitch_id):
    """
    Get a user document by Twitch ID
    
    Args:
        twitch_id (str): Twitch user ID
        
    Returns:
        dict: User document or None if not found
    """
    # If MongoDB is not available, return None
    if users_collection is None:
        logger.warning("MongoDB users collection is not available")
        return None
        
    try:
        return await users_collection.find_one({"twitch_id": twitch_id})
    except Exception as e:
        logger.error(f"Error getting user by Twitch ID: {str(e)}")
        return None

async def get_user_points(discord_id):
    """
    Get a user's points and rank
    
    Args:
        discord_id (str): Discord user ID
        
    Returns:
        dict: User points information
    """
    # If MongoDB is not available, return default values
    if users_collection is None:
        logger.warning("MongoDB users collection is not available, returning default user points")
        return {"points": 0, "rank": "New Member", "next_rank": "Novice", "next_rank_points": POINTS_ROLES["Novice"]}
        
    try:
        user = await get_user(discord_id)
        
        # If user doesn't exist, create them
        if not user:
            user = {
                "discord_id": discord_id,
                "points": 0,
                "transactions": [],
                "created_at": datetime.utcnow()
            }
            await users_collection.insert_one(user)
        
        # Get the user's rank
        points = user.get("points", 0)
        rank, next_rank, next_rank_points = _get_rank_from_points(points)
        
        return {
            "points": points,
            "rank": rank,
            "next_rank": next_rank,
            "next_rank_points": next_rank_points
        }
    except Exception as e:
        logger.error(f"Error getting user points: {str(e)}")
        return {"points": 0, "rank": "New Member", "next_rank": "Novice", "next_rank_points": POINTS_ROLES["Novice"]}

async def update_user_points(discord_id, points_to_add, reason=None, awarded_by=None):
    """
    Update a user's points
    
    Args:
        discord_id (str): Discord user ID
        points_to_add (int): Number of points to add
        reason (str, optional): Reason for the points
        awarded_by (str, optional): Discord ID of the user who awarded the points
        
    Returns:
        dict: Result of the operation
    """
    # If MongoDB is not available, return a graceful error
    if users_collection is None:
        logger.warning("MongoDB users collection is not available, cannot update points")
        return {
            "success": False, 
            "message": "Points system temporarily unavailable", 
            "fallback": True
        }
        
    try:
        # Get the user, create if doesn't exist
        user = await get_user(discord_id)
        
        if not user:
            user = {
                "discord_id": discord_id,
                "points": 0,
                "transactions": [],
                "created_at": datetime.utcnow()
            }
            await users_collection.insert_one(user)
        
        # Calculate new points
        current_points = user.get("points", 0)
        new_points = current_points + points_to_add
        
        # Create transaction record
        transaction = {
            "amount": points_to_add,
            "reason": reason or "Points awarded",
            "awarded_by": awarded_by,
            "timestamp": datetime.utcnow()
        }
        
        # Update the user
        await users_collection.update_one(
            {"discord_id": discord_id},
            {
                "$set": {"points": new_points},
                "$push": {"transactions": transaction}
            },
            upsert=True
        )
        
        # Get the new rank
        rank, next_rank, next_rank_points = _get_rank_from_points(new_points)
        
        return {
            "success": True,
            "new_total": new_points,
            "rank": rank,
            "next_rank": next_rank,
            "next_rank_points": next_rank_points
        }
    except Exception as e:
        logger.error(f"Error updating user points: {str(e)}")
        return {"success": False, "message": str(e)}

async def link_twitch_account(discord_id, twitch_id, twitch_username):
    """
    Link a Discord account to a Twitch account
    
    Args:
        discord_id (str): Discord user ID
        twitch_id (str): Twitch user ID
        twitch_username (str): Twitch username
        
    Returns:
        dict: Result of the operation
    """
    # If MongoDB is not available, return a graceful error
    if users_collection is None:
        logger.warning("MongoDB users collection is not available, cannot link Twitch account")
        return {
            "success": False, 
            "message": "Twitch linking temporarily unavailable", 
            "fallback": True
        }
        
    try:
        # Check if there's already a user with this Twitch ID
        existing_twitch_user = await get_user_by_twitch_id(twitch_id)
        
        if existing_twitch_user and existing_twitch_user["discord_id"] != discord_id:
            return {
                "success": False,
                "message": "This Twitch account is already linked to a different Discord user."
            }
        
        # Update or create the user
        await users_collection.update_one(
            {"discord_id": discord_id},
            {
                "$set": {
                    "twitch_id": twitch_id,
                    "twitch_username": twitch_username,
                    "twitch_linked_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error linking Twitch account: {str(e)}")
        return {"success": False, "message": str(e)}

async def get_leaderboard(limit=10):
    """
    Get the top users by points
    
    Args:
        limit (int): Number of users to return
        
    Returns:
        list: Top users
    """
    # If MongoDB is not available, return an empty list
    if users_collection is None:
        logger.warning("MongoDB users collection is not available, returning empty leaderboard")
        return []
        
    try:
        cursor = users_collection.find(
            {"points": {"$gt": 0}}
        ).sort("points", -1).limit(limit)
        
        leaderboard = []
        async for user in cursor:
            rank, _, _ = _get_rank_from_points(user["points"])
            leaderboard.append({
                "discord_id": user["discord_id"],
                "points": user["points"],
                "rank": rank
            })
        
        return leaderboard
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return []

async def add_mod_review(discord_id, discord_name, mod_name, rating, review_text):
    """
    Add a mod review
    
    Args:
        discord_id (str): Discord user ID
        discord_name (str): Discord username
        mod_name (str): Name of the mod
        rating (int): Rating (1-5)
        review_text (str): Review text
        
    Returns:
        dict: Result of the operation
    """
    # If MongoDB is not available, return a graceful error
    if mod_reviews_collection is None:
        logger.warning("MongoDB mod_reviews collection is not available, cannot add review")
        return {
            "success": False, 
            "message": "Review system temporarily unavailable", 
            "fallback": True
        }
        
    try:
        # Check if user has already reviewed this mod
        existing_review = await mod_reviews_collection.find_one({
            "discord_id": discord_id,
            "mod_name": mod_name
        })
        
        if existing_review:
            # Update the existing review
            await mod_reviews_collection.update_one(
                {"_id": existing_review["_id"]},
                {
                    "$set": {
                        "rating": rating,
                        "review_text": review_text,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Create a new review
            review = {
                "discord_id": discord_id,
                "discord_name": discord_name,
                "mod_name": mod_name,
                "rating": rating,
                "review_text": review_text,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await mod_reviews_collection.insert_one(review)
        
        # Reward the user with points for the review (only for new reviews)
        if not existing_review:
            await update_user_points(
                discord_id=discord_id,
                points_to_add=5,
                reason=f"Submitted review for mod: {mod_name}"
            )
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error adding mod review: {str(e)}")
        return {"success": False, "message": str(e)}

async def get_mod_reviews(mod_name):
    """
    Get reviews for a mod
    
    Args:
        mod_name (str): Name of the mod
        
    Returns:
        list: Reviews for the mod
    """
    # If MongoDB is not available, return an empty list
    if mod_reviews_collection is None:
        logger.warning("MongoDB mod_reviews collection is not available, returning empty reviews")
        return []
        
    try:
        cursor = mod_reviews_collection.find(
            {"mod_name": {"$regex": f"^{mod_name}$", "$options": "i"}}
        ).sort("created_at", -1)
        
        reviews = []
        async for review in cursor:
            reviews.append({
                "discord_id": review["discord_id"],
                "discord_name": review["discord_name"],
                "rating": review["rating"],
                "review_text": review["review_text"],
                "created_at": review["created_at"]
            })
        
        return reviews
    except Exception as e:
        logger.error(f"Error getting mod reviews: {str(e)}")
        return []

async def add_mod_suggestion(discord_id, discord_name, title, description, ai_feedback=None):
    """
    Add a mod suggestion
    
    Args:
        discord_id (str): Discord user ID
        discord_name (str): Discord username
        title (str): Suggestion title
        description (str): Suggestion description
        ai_feedback (str, optional): AI-generated feedback
        
    Returns:
        dict: Result of the operation
    """
    # If MongoDB is not available, return a graceful error
    if mod_suggestions_collection is None:
        logger.warning("MongoDB mod_suggestions collection is not available, cannot add suggestion")
        return {
            "success": False, 
            "message": "Suggestion system temporarily unavailable", 
            "fallback": True
        }
        
    try:
        suggestion = {
            "discord_id": discord_id,
            "discord_name": discord_name,
            "title": title,
            "description": description,
            "ai_feedback": ai_feedback,
            "created_at": datetime.utcnow()
        }
        
        await mod_suggestions_collection.insert_one(suggestion)
        
        # Reward the user with points for the suggestion
        await update_user_points(
            discord_id=discord_id,
            points_to_add=10,
            reason=f"Submitted mod suggestion: {title}"
        )
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error adding mod suggestion: {str(e)}")
        return {"success": False, "message": str(e)}

async def get_mod_suggestions(limit=5):
    """
    Get recent mod suggestions
    
    Args:
        limit (int): Number of suggestions to return
        
    Returns:
        list: Recent suggestions
    """
    # If MongoDB is not available, return an empty list
    if mod_suggestions_collection is None:
        logger.warning("MongoDB mod_suggestions collection is not available, returning empty suggestions")
        return []
        
    try:
        cursor = mod_suggestions_collection.find().sort("created_at", -1).limit(limit)
        
        suggestions = []
        async for suggestion in cursor:
            suggestions.append({
                "discord_id": suggestion["discord_id"],
                "discord_name": suggestion["discord_name"],
                "title": suggestion["title"],
                "description": suggestion["description"],
                "ai_feedback": suggestion.get("ai_feedback"),
                "created_at": suggestion["created_at"]
            })
        
        return suggestions
    except Exception as e:
        logger.error(f"Error getting mod suggestions: {str(e)}")
        return []
