from flask import render_template, jsonify, request, flash, redirect, url_for
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

@app.route('/update/appearance', methods=['POST'])
@login_required
def update_appearance():
    """Update user theme preference via form submission"""
    theme = request.form.get('theme_preference', 'dark')
    
    # Validate theme
    valid_themes = ['light', 'dark', 'space', 'neon', 'contrast']
    if theme not in valid_themes:
        flash('Invalid theme selection', 'danger')
        return redirect(url_for('account_settings'))
    
    # Check if theme is premium and user has access
    premium_themes = ['space', 'neon', 'contrast']
    if theme in premium_themes and not current_user.is_premium:
        flash('Premium required for this theme', 'warning')
        return redirect(url_for('account_settings'))
    
    try:
        current_user.theme_preference = theme
        db.session.commit()
        flash('Theme updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating theme: {str(e)}")
        flash(f'Error updating theme: {str(e)}', 'danger')
    
    return redirect(url_for('account_settings'))

@app.route('/update/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        # Update user profile fields
        current_user.username = request.form.get('username', current_user.username)
        current_user.email = request.form.get('email', current_user.email)
        current_user.bio = request.form.get('bio', current_user.bio or '')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('account_settings'))