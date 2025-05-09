import os
import logging
from flask import Flask, render_template, jsonify, redirect, url_for
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

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

# MongoDB setup
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
mod_reviews_collection = db["mod_reviews"]
mod_suggestions_collection = db["mod_suggestions"]

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

# Routes
@app.route('/')
def index():
    return render_template('index.html', title="AstroBot Dashboard")

@app.route('/api/stats')
def get_stats():
    # Get statistics about the bot usage and community
    async def get_data():
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
            ]
        }
    
    try:
        stats = run_async(get_data())
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/reviews')
def reviews():
    return render_template('reviews.html', title="Mod Reviews")

@app.route('/api/reviews')
def get_reviews():
    async def get_data():
        cursor = mod_reviews_collection.find().sort("created_at", -1).limit(10)
        reviews = await cursor.to_list(length=10)
        
        # Convert ObjectId to string
        for review in reviews:
            review["_id"] = str(review["_id"])
            review["created_at"] = review["created_at"].isoformat()
            if "updated_at" in review:
                review["updated_at"] = review["updated_at"].isoformat()
        
        return reviews
    
    try:
        reviews = run_async(get_data())
        return jsonify(reviews)
    except Exception as e:
        logger.error(f"Error getting reviews: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html', title="Mod Suggestions")

@app.route('/api/suggestions')
def get_suggestions():
    async def get_data():
        cursor = mod_suggestions_collection.find().sort("created_at", -1).limit(10)
        suggestions = await cursor.to_list(length=10)
        
        # Convert ObjectId to string
        for suggestion in suggestions:
            suggestion["_id"] = str(suggestion["_id"])
            suggestion["created_at"] = suggestion["created_at"].isoformat()
        
        return suggestions
    
    try:
        suggestions = run_async(get_data())
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', title="Community Leaderboard")

@app.route('/api/leaderboard')
def get_leaderboard():
    async def get_data():
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
    
    try:
        leaderboard = run_async(get_data())
        return jsonify(leaderboard)
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return jsonify({"error": str(e)}), 500

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