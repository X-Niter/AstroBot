import os
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import traceback
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

from config import MONGODB_URI, DB_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Configure PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///astrobot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import WebsiteUser
    return WebsiteUser.query.get(int(user_id))

# Create all database tables
with app.app_context():
    try:
        # Import models to register them with SQLAlchemy
        import models
        db.create_all()
        logger.info("PostgreSQL database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        logger.error(traceback.format_exc())

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
mongo_db = None
users_collection = None
mod_reviews_collection = None
mod_suggestions_collection = None
mongodb_available = False

# MongoDB setup - with error handling
try:
    # Use direct connection approach
    connection_params = {
        'serverSelectionTimeoutMS': 5000,
        'connectTimeoutMS': 5000,
        'socketTimeoutMS': 5000,
        'retryWrites': True,
        'retryReads': True
    }
    
    # Use Postgres for now since we're hitting MongoDB connection issues
    logger.info("Setting up SQLite as the database for now")
    mongodb_available = False
    
    # Initialize empty collections references
    client = None
    mongo_db = None
    users_collection = None
    mod_reviews_collection = None
    mod_suggestions_collection = None
    
    # Log the configuration
    logger.info("MongoDB temporarily disabled - using PostgreSQL for all functionality")
        
except Exception as e:
    logger.error(f"MongoDB setup error: {e}")
    logger.error(traceback.format_exc())
    mongodb_available = False

# Routes
@app.route('/')
def index():
    return render_template('index.html', title="Dashboard")

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    from forms import LoginForm
    from models import WebsiteUser
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = WebsiteUser.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html', title="Login", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    from forms import RegisterForm
    from models import WebsiteUser
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = WebsiteUser.query.filter((WebsiteUser.username == form.username.data) | 
                                        (WebsiteUser.email == form.email.data)).first()
        if user:
            if user.username == form.username.data:
                flash('Username already exists', 'danger')
            else:
                flash('Email already exists', 'danger')
        else:
            new_user = WebsiteUser(
                username=form.username.data,
                email=form.email.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('auth/register.html', title="Register", form=form)

# Documentation routes
@app.route('/documentation')
def documentation_index():
    return render_template('documentation/index.html', title="Documentation")

@app.route('/documentation/<page_type>/<page_name>')
def documentation_page(page_type, page_name):
    return render_template(f'documentation/{page_type}/{page_name}.html', 
                          title=f"Documentation - {page_name.replace('_', ' ').title()}")

@app.route('/api/documentation/feedback', methods=['POST'])
def documentation_feedback():
    from models import DocumentationFeedback
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    try:
        feedback = DocumentationFeedback(
            page_path=data.get('page', ''),
            helpful=data.get('helpful', False),
            comment=data.get('comment', ''),
            user_id=current_user.id if current_user.is_authenticated else None,
            ip_address=request.remote_addr
        )
        db.session.add(feedback)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving documentation feedback: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Onboarding wizard routes
@app.route('/onboarding')
def onboarding_wizard():
    """Renders the AI onboarding wizard page"""
    return render_template('onboarding/wizard.html', title="AstroBot AI Onboarding Wizard")

@app.route('/api/onboarding/configure', methods=['POST'])
def onboarding_configure():
    """Process configuration data from the onboarding wizard
    
    This endpoint can be accessed by both authenticated and non-authenticated users.
    Authenticated users will have their user ID associated with the configuration.
    """
    from services.onboarding_service import OnboardingService
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
    try:
        # Get optional CSRF token from header
        csrf_token = request.headers.get('X-CSRFToken')
        
        # Log the received configuration data
        logger.info(f"Received configuration data: {json.dumps(data)}")
        
        # Process the configuration with the OnboardingService
        user_id = current_user.id if current_user.is_authenticated else None
        result = OnboardingService.process_configuration(data, user_id)
        
        # Return the result with a 200 OK status
        return jsonify(result)
    except Exception as e:
        # Log the full traceback for debugging
        logger.error(f"Error processing onboarding configuration: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return an error response
        return jsonify({
            'status': 'error', 
            'message': f"Failed to process configuration: {str(e)}"
        }), 500

# Feedback route
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    from forms import FeedbackForm
    from models import Feedback
    
    form = FeedbackForm()
    if form.validate_on_submit():
        try:
            new_feedback = Feedback(
                feedback_type=form.feedback_type.data,
                feature_category=form.feature_category.data if form.feature_category.data else None,
                subject=form.subject.data,
                message=form.message.data,
                contact_info=form.contact_info.data,
                can_contact=form.can_contact.data,
                user_id=current_user.id if current_user.is_authenticated else None,
                discord_id=current_user.discord_id if current_user.is_authenticated and hasattr(current_user, 'discord_id') else None,
                discord_username=None  # Would be set from Discord OAuth in a real implementation
            )
            db.session.add(new_feedback)
            db.session.commit()
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            flash(f'Error submitting feedback: {str(e)}', 'danger')
    
    return render_template('feedback.html', title="Feedback & Suggestions", form=form)

@app.route('/api/status')
def api_status():
    """Return the overall status of the application"""
    return jsonify({
        "web_status": "online",
        "mongodb_connected": mongodb_available,
        "bot_running": True,
        "api_version": "1.0.0",
        "server_time": datetime.now().isoformat()
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
    """Bot settings dashboard"""
    # Get servers where user is owner
    if current_user.is_authenticated:
        servers = DiscordServer.query.filter_by(owner_id=current_user.id).all()
    else:
        servers = []
    
    return render_template('discord/settings.html', 
                          title="Bot Settings",
                          servers=servers)

@app.route('/discord/commands')
def commands_dashboard():
    return render_template('discord/commands.html', title="Commands")

@app.route('/discord/permissions')
def permissions():
    return render_template('discord/permissions.html', title="Permissions")

@app.route('/server/<server_id>/customize', methods=['GET', 'POST'])
@login_required
def bot_customization(server_id):
    """Customize bot appearance for a specific server (premium feature)"""
    # Get the server
    server = DiscordServer.query.filter_by(server_id=server_id).first_or_404()
    
    # Check if user has permission to customize this server's bot
    if server.owner_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to customize this server.', 'danger')
        return redirect(url_for('index'))
    
    # Get existing customization if any
    customization = BotCustomization.query.filter_by(server_id=server.id).first()
    
    # Handle form submission
    if request.method == 'POST':
        if not server.can_customize_bot:
            flash('Bot customization is a premium feature. Upgrade to access this feature.', 'warning')
            return redirect(url_for('premium_plans'))
        
        # Create or update customization
        if customization is None:
            customization = BotCustomization(
                server_id=server.id,
                created_by_id=current_user.id
            )
            db.session.add(customization)
        
        # Update fields
        customization.custom_name = request.form.get('custom_name', '')
        customization.custom_avatar_url = request.form.get('custom_avatar_url', '')
        customization.custom_status = request.form.get('custom_status', '')
        customization.custom_playing = request.form.get('custom_playing', '')
        customization.theme_color = request.form.get('theme_color', '#5865F2')
        customization.custom_prefix = request.form.get('custom_prefix', '')
        
        try:
            db.session.commit()
            flash('Bot customization saved successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving bot customization: {str(e)}")
            flash(f'Error saving customization: {str(e)}', 'danger')
        
        return redirect(url_for('bot_customization', server_id=server_id))
    
    # Pass current time for preview
    now = datetime.now()
    
    return render_template('server/bot_customization.html',
                          title="Bot Customization",
                          server=server,
                          customization=customization,
                          now=now)

@app.route('/discord/analytics')
def discord_analytics():
    return render_template('discord/analytics.html', title="Discord Bot Analytics")

@app.route('/analytics')
def analytics():
    return render_template('analytics/dashboard.html', title="Analytics Dashboard")

@app.route('/analytics/commands')
def commands_analytics():
    return render_template('analytics/commands.html', title="Command Analytics")

@app.route('/analytics/ai')
def ai_analytics():
    return render_template('analytics/ai.html', title="AI Usage Analytics")

@app.route('/analytics/community')
def community_analytics():
    return render_template('analytics/community.html', title="Community Analytics")

@app.route('/analytics/moderation')
def moderation_analytics():
    return render_template('analytics/moderation.html', title="Moderation Analytics")

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

# Admin routes
@app.route('/admin/premium-users')
@login_required
def premium_users():
    """Admin panel for managing premium users"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    users = WebsiteUser.query.all()
    premium_features = PremiumFeature.query.all()
    
    return render_template('admin/premium_users.html', 
                          title="Premium User Management", 
                          users=users, 
                          features=premium_features)

@app.route('/admin/premium-features')
@login_required
def premium_features():
    """Admin panel for managing premium features"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    features = PremiumFeature.query.all()
    return render_template('admin/premium_features.html', 
                          title="Premium Features Management", 
                          features=features)

@app.route('/admin/server-showcase')
@login_required
def server_showcase():
    """Admin panel for managing server showcase"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    servers = DiscordServer.query.all()
    return render_template('admin/server_showcase.html', 
                          title="Server Showcase Management", 
                          servers=servers)

@app.route('/api/admin/toggle-premium', methods=['POST'])
@login_required
def toggle_premium():
    """Toggle premium status for a user"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    if not data or 'user_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    try:
        user = WebsiteUser.query.get(data['user_id'])
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        user.is_premium = not user.is_premium
        if user.is_premium and not user.premium_since:
            user.premium_since = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': f"User {user.username} premium status set to {user.is_premium}",
            'is_premium': user.is_premium
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling premium status: {str(e)}")
        return jsonify({'status': 'error', 'message': f"Error: {str(e)}"}), 500

@app.route('/api/admin/assign-feature', methods=['POST'])
@login_required
def assign_premium_feature():
    """Assign a premium feature to a user"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    if not data or 'user_id' not in data or 'feature_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    try:
        user = WebsiteUser.query.get(data['user_id'])
        feature = PremiumFeature.query.get(data['feature_id'])
        
        if not user or not feature:
            return jsonify({'status': 'error', 'message': 'User or feature not found'}), 404
        
        # Check if user already has this feature
        existing = UserPremiumFeature.query.filter_by(
            user_id=user.id, feature_id=feature.id
        ).first()
        
        if existing:
            return jsonify({'status': 'error', 'message': 'User already has this feature'}), 400
        
        # Create new user-feature association
        expires_at = None
        if data.get('expires_days'):
            expires_at = datetime.utcnow() + timedelta(days=int(data['expires_days']))
        
        user_feature = UserPremiumFeature(
            user_id=user.id,
            feature_id=feature.id,
            assigned_by_id=current_user.id,
            expires_at=expires_at
        )
        
        db.session.add(user_feature)
        
        # Ensure user is marked as premium
        if not user.is_premium:
            user.is_premium = True
            user.premium_since = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f"Feature '{feature.name}' assigned to {user.username}"
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error assigning premium feature: {str(e)}")
        return jsonify({'status': 'error', 'message': f"Error: {str(e)}"}), 500

@app.route('/api/admin/remove-feature', methods=['POST'])
@login_required
def remove_premium_feature():
    """Remove a premium feature from a user"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    if not data or 'user_feature_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    try:
        user_feature = UserPremiumFeature.query.get(data['user_feature_id'])
        if not user_feature:
            return jsonify({'status': 'error', 'message': 'User feature not found'}), 404
        
        feature_name = user_feature.feature.name
        username = user_feature.user.username
        
        db.session.delete(user_feature)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f"Feature '{feature_name}' removed from {username}"
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing premium feature: {str(e)}")
        return jsonify({'status': 'error', 'message': f"Error: {str(e)}"}), 500

@app.route('/admin/premium-features/add', methods=['POST'])
@login_required
def add_premium_feature():
    """Add a new premium feature"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    try:
        name = request.form.get('name')
        feature_key = request.form.get('feature_key')
        description = request.form.get('description', '')
        tier = request.form.get('tier', 'standard')
        
        # Check if feature with this key already exists
        existing = PremiumFeature.query.filter_by(feature_key=feature_key).first()
        if existing:
            flash(f'A feature with key "{feature_key}" already exists.', 'danger')
            return redirect(url_for('premium_features'))
        
        # Create new feature
        feature = PremiumFeature(
            name=name,
            feature_key=feature_key,
            description=description,
            tier=tier,
            is_active=True,
            created_by_id=current_user.id
        )
        
        db.session.add(feature)
        db.session.commit()
        
        flash(f'Premium feature "{name}" has been added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding premium feature: {str(e)}")
        flash(f'Error adding premium feature: {str(e)}', 'danger')
    
    return redirect(url_for('premium_features'))

@app.route('/admin/premium-features/update', methods=['POST'])
@login_required
def update_premium_feature():
    """Update an existing premium feature"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    try:
        feature_id = request.form.get('feature_id')
        name = request.form.get('name')
        feature_key = request.form.get('feature_key')
        description = request.form.get('description', '')
        tier = request.form.get('tier', 'standard')
        
        feature = PremiumFeature.query.get(feature_id)
        if not feature:
            flash('Feature not found.', 'danger')
            return redirect(url_for('premium_features'))
        
        # Check if another feature with this key already exists
        if feature.feature_key != feature_key:
            existing = PremiumFeature.query.filter_by(feature_key=feature_key).first()
            if existing and existing.id != int(feature_id):
                flash(f'Another feature with key "{feature_key}" already exists.', 'danger')
                return redirect(url_for('premium_features'))
        
        # Update feature
        feature.name = name
        feature.feature_key = feature_key
        feature.description = description
        feature.tier = tier
        
        db.session.commit()
        
        flash(f'Premium feature "{name}" has been updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating premium feature: {str(e)}")
        flash(f'Error updating premium feature: {str(e)}', 'danger')
    
    return redirect(url_for('premium_features'))

@app.route('/api/admin/toggle-feature', methods=['POST'])
@login_required
def toggle_feature():
    """Toggle active status for a premium feature"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    if not data or 'feature_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    try:
        feature = PremiumFeature.query.get(data['feature_id'])
        if not feature:
            return jsonify({'status': 'error', 'message': 'Feature not found'}), 404
        
        feature.is_active = data.get('is_active', not feature.is_active)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f"Feature '{feature.name}' is now {'active' if feature.is_active else 'inactive'}"
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling feature status: {str(e)}")
        return jsonify({'status': 'error', 'message': f"Error: {str(e)}"}), 500

@app.route('/api/admin/delete-feature', methods=['POST'])
@login_required
def delete_feature():
    """Delete a premium feature"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    if not data or 'feature_id' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    try:
        feature = PremiumFeature.query.get(data['feature_id'])
        if not feature:
            return jsonify({'status': 'error', 'message': 'Feature not found'}), 404
        
        # Check if feature is assigned to any users
        user_features = UserPremiumFeature.query.filter_by(feature_id=feature.id).count()
        if user_features > 0:
            return jsonify({
                'status': 'error',
                'message': f"Cannot delete feature '{feature.name}' because it is assigned to {user_features} users"
            }), 400
        
        feature_name = feature.name
        db.session.delete(feature)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f"Feature '{feature_name}' has been deleted"
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting feature: {str(e)}")
        return jsonify({'status': 'error', 'message': f"Error: {str(e)}"}), 500

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

# Analytics API endpoints
@app.route('/api/analytics/dashboard')
def get_analytics_dashboard():
    try:
        # Get the days parameter, defaulting to 30
        days = int(request.args.get('days', 30))
        
        # Create sample data (for demo purposes)
        dashboard_data = {
            'command_count': 3254,
            'ai_request_count': 1245,
            'ai_token_usage': 2345678,
            'user_count': 426,
            'points_awarded': 32456,
            'point_transactions': 1234,
            'moderation_actions': 87,
            'stream_notifications': 56,
            'usage_over_time': generate_time_data(days),
            'days': days
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Error getting analytics dashboard data: {str(e)}")
        return jsonify({
            "error": f"Error getting analytics data: {str(e)}",
            "days": int(request.args.get('days', 30))
        })

@app.route('/api/analytics/commands')
def get_analytics_commands():
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        guild_id = request.args.get('guild_id')
        category = request.args.get('category')
        
        # Create sample data (for demo purposes)
        command_data = {
            'total_commands': 3254,
            'unique_commands': 24,
            'success_rate': 97.8,
            'command_usage': [
                {'name': 'ask', 'count': 523},
                {'name': 'server-status', 'count': 412},
                {'name': 'idea', 'count': 287},
                {'name': 'tutorial', 'count': 236},
                {'name': 'whitelist-add', 'count': 195},
                {'name': 'fix', 'count': 189},
                {'name': 'points', 'count': 174},
                {'name': 'leaderboard', 'count': 167},
                {'name': 'find', 'count': 156},
                {'name': 'stream', 'count': 138}
            ],
            'category_usage': [
                {'category': 'ai', 'count': 1235},
                {'category': 'minecraft', 'count': 876},
                {'category': 'community', 'count': 645},
                {'category': 'twitch', 'count': 437},
                {'category': 'custom', 'count': 61}
            ],
            'time_usage': generate_time_data(days),
            'days': days
        }
        
        return jsonify(command_data)
    except Exception as e:
        logger.error(f"Error getting command analytics data: {str(e)}")
        return jsonify({
            "error": f"Error getting command analytics data: {str(e)}",
            "days": int(request.args.get('days', 30))
        })

@app.route('/api/analytics/ai')
def get_analytics_ai():
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        guild_id = request.args.get('guild_id')
        
        # Create sample data (for demo purposes)
        ai_data = {
            'total_tokens': 2345678,
            'total_requests': 1245,
            'avg_tokens_per_request': 1884.1,
            'success_rate': 99.2,
            'model_usage': [
                {'model': 'gpt-4o', 'tokens': 1456789, 'count': 765, 'percentage': 62.1},
                {'model': 'claude-3.5-sonnet', 'tokens': 843256, 'count': 452, 'percentage': 35.9},
                {'model': 'dall-e-3', 'tokens': 45633, 'count': 28, 'percentage': 2.0}
            ],
            'feature_usage': [
                {'feature': 'ask', 'tokens': 986532, 'count': 542, 'percentage': 42.0},
                {'feature': 'idea', 'tokens': 432187, 'count': 287, 'percentage': 18.4},
                {'feature': 'fix', 'tokens': 356942, 'count': 189, 'percentage': 15.2},
                {'feature': 'tutorial', 'tokens': 421348, 'count': 157, 'percentage': 18.0},
                {'feature': 'generate', 'tokens': 148669, 'count': 70, 'percentage': 6.4}
            ],
            'time_usage': generate_time_data(days, True),
            'days': days
        }
        
        return jsonify(ai_data)
    except Exception as e:
        logger.error(f"Error getting AI analytics data: {str(e)}")
        return jsonify({
            "error": f"Error getting AI analytics data: {str(e)}",
            "days": int(request.args.get('days', 30))
        })

@app.route('/api/analytics/community')
def get_analytics_community():
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        guild_id = request.args.get('guild_id')
        
        # Create sample data (for demo purposes)
        community_data = {
            'total_points': 32456,
            'transaction_count': 1234,
            'avg_rating': 4.3,
            'review_count': 87,
            'suggestion_count': 56,
            'source_breakdown': [
                {'source': 'twitch', 'points': 15678, 'count': 543, 'percentage': 48.3},
                {'source': 'discord', 'points': 9845, 'count': 342, 'percentage': 30.3},
                {'source': 'minecraft', 'points': 4587, 'count': 223, 'percentage': 14.1},
                {'source': 'admin', 'points': 2346, 'count': 126, 'percentage': 7.3}
            ],
            'top_earners': [
                {'user_id': '123456789', 'username': 'User1', 'points': 3245},
                {'user_id': '234567890', 'username': 'User2', 'points': 2876},
                {'user_id': '345678901', 'username': 'User3', 'points': 2543},
                {'user_id': '456789012', 'username': 'User4', 'points': 2187},
                {'user_id': '567890123', 'username': 'User5', 'points': 1945}
            ],
            'time_data': generate_time_data(days),
            'days': days
        }
        
        return jsonify(community_data)
    except Exception as e:
        logger.error(f"Error getting community analytics data: {str(e)}")
        return jsonify({
            "error": f"Error getting community analytics data: {str(e)}",
            "days": int(request.args.get('days', 30))
        })

@app.route('/api/analytics/moderation')
def get_analytics_moderation():
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        guild_id = request.args.get('guild_id')
        
        # Create sample data (for demo purposes)
        moderation_data = {
            'total_actions': 87,
            'active_mutes': 3,
            'active_bans': 11,
            'action_breakdown': [
                {'type': 'warning', 'count': 42, 'percentage': 48.3},
                {'type': 'mute', 'count': 21, 'percentage': 24.1},
                {'type': 'ban', 'count': 15, 'percentage': 17.2},
                {'type': 'kick', 'count': 5, 'percentage': 5.8},
                {'type': 'unmute', 'count': 4, 'percentage': 4.6}
            ],
            'top_moderators': [
                {'moderator_id': '123456789', 'username': 'AdminUser1', 'action_count': 32, 'percentage': 36.8},
                {'moderator_id': '234567890', 'username': 'ModUser2', 'action_count': 24, 'percentage': 27.6},
                {'moderator_id': '345678901', 'username': 'ModUser3', 'action_count': 18, 'percentage': 20.7},
                {'moderator_id': '456789012', 'username': 'ModUser4', 'action_count': 13, 'percentage': 14.9}
            ],
            'time_data': generate_time_data(days),
            'days': days
        }
        
        return jsonify(moderation_data)
    except Exception as e:
        logger.error(f"Error getting moderation analytics data: {str(e)}")
        return jsonify({
            "error": f"Error getting moderation analytics data: {str(e)}",
            "days": int(request.args.get('days', 30))
        })

# Helper function to generate time data for analytics
def generate_time_data(days, is_ai=False):
    data = []
    now = datetime.datetime.now()
    
    for i in range(days + 1):
        date = now - datetime.timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        if is_ai:
            # Generate random data for AI
            from random import randint
            count = randint(10, 60)
            tokens = count * randint(1500, 2000)
            data.append({
                'date': date_str,
                'count': count,
                'tokens': tokens
            })
        else:
            # Generate random data for general usage
            from random import randint
            data.append({
                'date': date_str,
                'count': randint(50, 200)
            })
    
    # Reverse to get chronological order
    data.reverse()
    return data

# Admin routes
@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html', title="Admin Dashboard")

@app.route('/admin/deployment')
def admin_deployment():
    return render_template('admin/deployment.html', title="Intelligent Deployment")

@app.route('/admin/shards')
def admin_shards():
    return render_template('admin/shards.html', title="Shard Management")

@app.route('/admin/deployments-history')
def admin_deployments_history():
    return render_template('admin/deployments_history.html', title="Deployment History")

@app.route('/admin/alerts')
def admin_alerts():
    return render_template('admin/alerts.html', title="System Alerts")

@app.route('/admin/logs')
def admin_logs():
    return render_template('admin/logs.html', title="System Logs")

@app.route('/admin/settings')
def admin_settings():
    return render_template('admin/settings.html', title="System Settings")

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