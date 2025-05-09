import os
import logging
from flask import Flask, render_template, jsonify, redirect, url_for
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import traceback
import datetime

from config import MONGODB_URI, DB_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Create async event loop for MongoDB queries
def get_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# Helper function to run async functions
def run_async(coro):
    loop = get_event_loop()
    return loop.run_until_complete(coro)

# Default collections as None
client = None
db = None
users_collection = None
mod_reviews_collection = None
mod_suggestions_collection = None
mongodb_available = False

# MongoDB setup - with error handling
try:
    # Connect with a shorter timeout for faster startup
    client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    
    # Collections
    users_collection = db["users"]
    mod_reviews_collection = db["mod_reviews"]
    mod_suggestions_collection = db["mod_suggestions"]
    
    # Test connection with a timeout
    async def test_connection():
        try:
            await client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False
    
    # Run the connection test
    connection_ok = run_async(test_connection())
    mongodb_available = connection_ok
    
    if mongodb_available:
        logger.info("MongoDB connection successful")
    else:
        logger.error("MongoDB connection test failed")
        
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")
    logger.error(traceback.format_exc())
    mongodb_available = False

# Routes
@app.route('/')
def index():
    return render_template('index.html', title="Dashboard")

@app.route('/api/status')
def api_status():
    """Return the overall status of the application"""
    return jsonify({
        "web_status": "online",
        "mongodb_connected": mongodb_available,
        "bot_running": True,
        "api_version": "1.0.0",
        "server_time": datetime.datetime.now().isoformat()
    })

# Minecraft management routes
@app.route('/minecraft/servers')
def minecraft_servers():
    return render_template('minecraft/servers.html', title="Minecraft Servers")

@app.route('/minecraft/whitelist')
def whitelist():
    return render_template('minecraft/whitelist.html', title="Whitelist Manager")

@app.route('/minecraft/console')
def console():
    return render_template('minecraft/console.html', title="Console Commands")

@app.route('/minecraft/plugins')
def plugins():
    return render_template('minecraft/plugins.html', title="Plugins & Mods")

# Discord bot management routes
@app.route('/discord/settings')
def bot_settings():
    return render_template('discord/settings.html', title="Bot Settings")

@app.route('/discord/commands')
def commands_dashboard():
    return render_template('discord/commands.html', title="Commands")

@app.route('/discord/permissions')
def permissions():
    return render_template('discord/permissions.html', title="Permissions")

@app.route('/discord/analytics')
def analytics():
    return render_template('discord/analytics.html', title="Bot Analytics")

# Twitch StreamSync routes
@app.route('/twitch/integration')
def twitch_integration():
    return render_template('twitch/integration.html', title="Twitch Integration")

@app.route('/twitch/points')
def points_settings():
    return render_template('twitch/points.html', title="Points & Rewards")

# AI generation routes
@app.route('/mods/ai-generator')
def ai_generator():
    return render_template('mods/ai_generator.html', title="AI Generation")

# Settings routes
@app.route('/settings/api-keys')
def api_settings():
    return render_template('settings/api_keys.html', title="API Keys")

@app.route('/settings/system')
def system_settings():
    return render_template('settings/system.html', title="System Settings")

@app.route('/settings/logs')
def logs():
    return render_template('settings/logs.html', title="System Logs")

@app.route('/api/stats')
def get_stats():
    # If MongoDB is not available, return default data
    if not mongodb_available:
        logger.warning("MongoDB not available, returning default data for stats")
        return jsonify({
            "user_count": 0,
            "review_count": 0,
            "suggestion_count": 0,
            "top_users": [],
            "connection_status": "MongoDB connection unavailable. Check your connection settings."
        })
    
    # Get statistics about the bot usage and community
    async def get_data():
        try:
            user_count = await users_collection.count_documents({})
            review_count = await mod_reviews_collection.count_documents({})
            suggestion_count = await mod_suggestions_collection.count_documents({})
            
            # Get top users
            cursor = users_collection.find().sort("points", -1).limit(5)
            top_users = await cursor.to_list(length=5)
            
            return {
                "user_count": user_count,
                "review_count": review_count,
                "suggestion_count": suggestion_count,
                "top_users": [
                    {"discord_id": user["discord_id"], "points": user["points"]} 
                    for user in top_users
                ],
                "connection_status": "connected"
            }
        except Exception as e:
            logger.error(f"Error getting MongoDB stats: {str(e)}")
            return {
                "user_count": 0,
                "review_count": 0,
                "suggestion_count": 0,
                "top_users": [],
                "connection_status": f"Error: {str(e)}"
            }
    
    try:
        stats = run_async(get_data())
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            "user_count": 0,
            "review_count": 0, 
            "suggestion_count": 0,
            "top_users": [],
            "connection_status": f"Error: {str(e)}"
        })

@app.route('/reviews')
def reviews():
    return render_template('reviews.html', title="Mod Reviews")

@app.route('/api/reviews')
def get_reviews():
    # If MongoDB is not available, return empty array
    if not mongodb_available:
        logger.warning("MongoDB not available, returning empty array for reviews")
        return jsonify([])
    
    async def get_data():
        try:
            cursor = mod_reviews_collection.find().sort("created_at", -1).limit(10)
            reviews = await cursor.to_list(length=10)
            
            # Convert ObjectId to string
            for review in reviews:
                review["_id"] = str(review["_id"])
                review["created_at"] = review["created_at"].isoformat()
                if "updated_at" in review:
                    review["updated_at"] = review["updated_at"].isoformat()
            
            return reviews
        except Exception as e:
            logger.error(f"Error getting reviews data: {str(e)}")
            return []
    
    try:
        reviews = run_async(get_data())
        return jsonify(reviews)
    except Exception as e:
        logger.error(f"Error getting reviews: {str(e)}")
        return jsonify([])

@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html', title="Mod Suggestions")

@app.route('/api/suggestions')
def get_suggestions():
    # If MongoDB is not available, return empty array
    if not mongodb_available:
        logger.warning("MongoDB not available, returning empty array for suggestions")
        return jsonify([])
    
    async def get_data():
        try:
            cursor = mod_suggestions_collection.find().sort("created_at", -1).limit(10)
            suggestions = await cursor.to_list(length=10)
            
            # Convert ObjectId to string
            for suggestion in suggestions:
                suggestion["_id"] = str(suggestion["_id"])
                suggestion["created_at"] = suggestion["created_at"].isoformat()
            
            return suggestions
        except Exception as e:
            logger.error(f"Error getting suggestions data: {str(e)}")
            return []
    
    try:
        suggestions = run_async(get_data())
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify([])

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', title="Community Leaderboard")

@app.route('/api/leaderboard')
def get_leaderboard():
    # If MongoDB is not available, return empty array
    if not mongodb_available:
        logger.warning("MongoDB not available, returning empty array for leaderboard")
        return jsonify([])
    
    async def get_data():
        try:
            cursor = users_collection.find({"points": {"$gt": 0}}).sort("points", -1).limit(20)
            users = await cursor.to_list(length=20)
            
            # Convert ObjectId to string and format data
            leaderboard = []
            for user in users:
                leaderboard.append({
                    "discord_id": user["discord_id"],
                    "points": user["points"],
                    "twitch_username": user.get("twitch_username", None),
                    "created_at": user["created_at"].isoformat()
                })
            
            return leaderboard
        except Exception as e:
            logger.error(f"Error getting leaderboard data: {str(e)}")
            return []
    
    try:
        leaderboard = run_async(get_data())
        return jsonify(leaderboard)
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return jsonify([])

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title="Page Not Found", error="404 - Page Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', title="Server Error", error="500 - Internal Server Error"), 500

if __name__ == '__main__':
    # This code won't run when using Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)