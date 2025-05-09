from flask import render_template, jsonify, request, flash
from flask_login import login_required, current_user
from app import app, db, logger

# Account settings routes
@app.route('/account/settings', methods=['GET'])
@login_required
def account_settings():
    """User account settings page"""
    # Get available themes
    themes = [
        {"id": "light", "name": "Light Mode", "description": "Clean light theme with blue accents", "premium": False},
        {"id": "dark", "name": "Dark Mode", "description": "Dark theme that's easier on the eyes", "premium": False},
        {"id": "space", "name": "Space Theme", "description": "Dark space-inspired theme with stars", "premium": True},
        {"id": "neon", "name": "Neon Theme", "description": "Vibrant neon colors on dark background", "premium": True},
        {"id": "contrast", "name": "High Contrast", "description": "High contrast theme for better accessibility", "premium": True}
    ]
    
    return render_template('account/settings.html', 
                          title="Account Settings",
                          themes=themes,
                          current_theme=current_user.theme_preference)

@app.route('/api/update-theme', methods=['POST'])
@login_required
def update_theme():
    """Update user theme preference"""
    data = request.json
    if not data or 'theme' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
    
    theme = data['theme']
    # Validate theme
    valid_themes = ['light', 'dark', 'space', 'neon', 'contrast']
    if theme not in valid_themes:
        return jsonify({'status': 'error', 'message': 'Invalid theme'}), 400
    
    # Check if theme is premium and user has access
    premium_themes = ['space', 'neon', 'contrast']
    if theme in premium_themes and not current_user.is_premium:
        return jsonify({'status': 'error', 'message': 'Premium required for this theme'}), 403
    
    try:
        current_user.theme_preference = theme
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': f'Theme updated to {theme}',
            'theme': theme
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating theme: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500