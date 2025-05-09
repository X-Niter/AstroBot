from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo, Regexp

class FeedbackForm(FlaskForm):
    """Form for user feedback and suggestions"""
    feedback_type = SelectField(
        'Feedback Type',
        choices=[
            ('bug_report', 'Bug Report'),
            ('feature_request', 'Feature Request'),
            ('improvement', 'Improvement Suggestion'),
            ('general_feedback', 'General Feedback'),
            ('question', 'Question')
        ],
        validators=[DataRequired()]
    )
    
    feature_category = SelectField(
        'Feature Category',
        choices=[
            ('moderation', 'Moderation System'),
            ('custom_commands', 'Custom Commands'),
            ('minecraft', 'Minecraft Integration'),
            ('twitch', 'Twitch Integration'),
            ('ai', 'AI Features'),
            ('music', 'Music Features'),
            ('web_dashboard', 'Web Dashboard'),
            ('api', 'API & Integrations'),
            ('other', 'Other')
        ]
    )
    
    subject = StringField(
        'Subject',
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    
    message = TextAreaField(
        'Message',
        validators=[DataRequired(), Length(min=10, max=2000)]
    )
    
    contact_info = StringField(
        'Contact Information',
        validators=[Optional(), Length(max=100)]
    )
    
    can_contact = BooleanField('Can Contact')


class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )


class RegisterForm(FlaskForm):
    """Form for user registration"""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)]
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )


class DocumentationFeedbackForm(FlaskForm):
    """Form for documentation page feedback"""
    helpful = BooleanField('Helpful')
    
    comment = TextAreaField(
        'Comment',
        validators=[Optional(), Length(max=1000)]
    )
    
    page_path = StringField('Page Path')


class ApiKeyForm(FlaskForm):
    """Form for generating API keys"""
    description = StringField(
        'Description',
        validators=[DataRequired(), Length(max=100)]
    )
    
    permissions = SelectField(
        'Permission Level',
        choices=[
            ('read', 'Read-only'),
            ('write', 'Read and Write'),
            ('admin', 'Full Admin Access')
        ],
        validators=[DataRequired()]
    )


class WebhookForm(FlaskForm):
    """Form for configuring webhooks"""
    name = StringField(
        'Webhook Name',
        validators=[DataRequired(), Length(max=50)]
    )
    
    url = StringField(
        'Webhook URL',
        validators=[DataRequired(), Length(max=200)]
    )
    
    event_type = SelectField(
        'Event Type',
        choices=[
            ('all', 'All Events'),
            ('moderation', 'Moderation Events'),
            ('user_join_leave', 'User Join/Leave Events'),
            ('message', 'Message Events'),
            ('command', 'Command Usage Events')
        ],
        validators=[DataRequired()]
    )
    
    active = BooleanField('Active')


class BotCustomizationForm(FlaskForm):
    """Form for customizing the bot appearance for premium servers"""
    custom_name = StringField(
        'Bot Name',
        validators=[Optional(), Length(min=3, max=32)]
    )
    
    custom_status = StringField(
        'Status Text',
        validators=[Optional(), Length(max=100)]
    )
    
    custom_playing = StringField(
        'Playing Status',
        validators=[Optional(), Length(max=100)]
    )
    
    theme_color = StringField(
        'Theme Color',
        validators=[
            Optional(), 
            Regexp(r'^#(?:[0-9a-fA-F]{3}){1,2}$', message='Must be a valid HEX color code (e.g. #7289DA)')
        ]
    )
    
    avatar_file = FileField(
        'Bot Avatar',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
        ]
    )