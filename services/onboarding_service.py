import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from app import db
from models import ServerConfiguration

logger = logging.getLogger(__name__)

class OnboardingService:
    """Service for handling the AI onboarding wizard configuration"""
    
    @staticmethod
    def process_configuration(config_data: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process and store the configuration data from the onboarding wizard
        
        Args:
            config_data: The configuration data from the onboarding wizard
            user_id: The ID of the user who created the configuration (if authenticated)
            
        Returns:
            Dict containing the status and any relevant information
        """
        try:
            logger.info(f"Processing onboarding configuration: {json.dumps(config_data)}")
            
            # Create a new server configuration
            config = ServerConfiguration(
                name=config_data.get('name', 'AstroBot Configuration'),
                server_purpose=config_data.get('server_purpose', 'community'),
                server_size=config_data.get('server_size', 'medium'),
                activity_level=config_data.get('activity_level', 'medium'),
                moderation_needs=config_data.get('moderation_needs', 'medium'),
                selected_features=json.dumps(config_data.get('features', [])),
                feature_settings=json.dumps(config_data.get('feature_settings', {})),
                additional_requirements=config_data.get('additional_requirements'),
                created_by_user_id=user_id
            )
            
            # Save configuration to database
            db.session.add(config)
            db.session.commit()
            
            # Configure specific features based on the selected features
            OnboardingService._configure_features(
                config, 
                config_data.get('features', []), 
                config_data.get('server_info', {})
            )
            
            # Mark configuration as completed
            config.status = 'configured'
            db.session.commit()
            
            return {
                'status': 'success',
                'config_id': config.id,
                'message': 'Configuration saved successfully'
            }
        
        except Exception as e:
            logger.error(f"Error processing configuration: {str(e)}")
            
            # Return error response
            return {
                'status': 'error',
                'message': f"Failed to process configuration: {str(e)}"
            }
    
    @staticmethod
    def _configure_features(config: ServerConfiguration, selected_features: List[str], server_info: Dict[str, Any]) -> None:
        """
        Configure specific features based on the selected features and server information
        
        Args:
            config: The ServerConfiguration object
            selected_features: List of selected feature names
            server_info: Dictionary containing server information
        """
        feature_settings = {}
        
        # Configure each selected feature
        if 'moderation' in selected_features:
            feature_settings['moderation'] = OnboardingService._configure_moderation(
                config, 
                server_info.get('moderation', {})
            )
        
        if 'commands' in selected_features:
            feature_settings['commands'] = OnboardingService._configure_custom_commands(
                config,
                server_info.get('commands', {})
            )
        
        if 'minecraft' in selected_features:
            feature_settings['minecraft'] = OnboardingService._configure_minecraft(
                config,
                server_info.get('minecraft', {})
            )
        
        if 'ai' in selected_features:
            feature_settings['ai'] = OnboardingService._configure_ai(
                config,
                server_info.get('ai', {})
            )
        
        if 'twitch' in selected_features:
            feature_settings['twitch'] = OnboardingService._configure_twitch(
                config,
                server_info.get('twitch', {})
            )
        
        if 'analytics' in selected_features:
            feature_settings['analytics'] = OnboardingService._configure_analytics(
                config,
                server_info.get('analytics', {})
            )
        
        # Update the configuration with feature settings
        config.feature_settings = json.dumps(feature_settings)
    
    @staticmethod
    def _configure_moderation(config: ServerConfiguration, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure moderation features based on settings"""
        moderation_config = {
            'sensitivity': settings.get('sensitivity', 'medium'),
            'auto_moderation': settings.get('autoModeration', True),
            'warning_system': settings.get('warningSystem', '3-strike'),
            'log_channel_enabled': True,
            'filter_words': settings.get('filterWords', True),
            'anti_spam': settings.get('antiSpam', True),
            'anti_raid': settings.get('antiRaid', True),
        }
        
        logger.info(f"Configured moderation settings: {json.dumps(moderation_config)}")
        return moderation_config
    
    @staticmethod
    def _configure_custom_commands(config: ServerConfiguration, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure custom commands based on settings"""
        commands_config = {
            'enable_custom_commands': settings.get('enableCustomCommands', True),
            'command_prefix': settings.get('commandPrefix', '!'),
            'enable_reaction_roles': settings.get('enableReactionRoles', True),
            'enable_autoresponders': settings.get('enableAutoresponders', True),
            'command_cooldowns': settings.get('enableCooldowns', True),
        }
        
        logger.info(f"Configured custom commands settings: {json.dumps(commands_config)}")
        return commands_config
    
    @staticmethod
    def _configure_minecraft(config: ServerConfiguration, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Minecraft integration based on settings"""
        minecraft_config = {
            'server_type': settings.get('serverType', 'vanilla'),
            'enable_whitelist': settings.get('whitelist', True),
            'enable_server_monitoring': settings.get('monitoring', True),
            'enable_mod_management': settings.get('modManagement', True),
            'enable_backups': settings.get('enableBackups', True),
            'enable_console_relay': settings.get('enableConsoleRelay', True),
        }
        
        logger.info(f"Configured Minecraft settings: {json.dumps(minecraft_config)}")
        return minecraft_config
    
    @staticmethod
    def _configure_ai(config: ServerConfiguration, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure AI features based on settings"""
        ai_config = {
            'enable_claude': settings.get('enableClaude', True),
            'enable_gpt4o': settings.get('enableGPT4o', True),
            'enable_image_generation': settings.get('enableImageGeneration', True),
            'enable_mod_generation': settings.get('enableModGeneration', True),
            'enable_ai_responses': settings.get('enableAIResponses', True),
            'content_filter_level': settings.get('contentFilterLevel', 'medium'),
        }
        
        logger.info(f"Configured AI settings: {json.dumps(ai_config)}")
        return ai_config
    
    @staticmethod
    def _configure_twitch(config: ServerConfiguration, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Twitch integration based on settings"""
        twitch_config = {
            'enable_stream_notifications': settings.get('enableStreamNotifications', True),
            'enable_points_system': settings.get('enablePointsSystem', True),
            'enable_chat_relay': settings.get('enableChatRelay', True),
            'auto_role_for_streamers': settings.get('autoRoleForStreamers', True),
            'enable_clip_sharing': settings.get('enableClipSharing', True),
        }
        
        logger.info(f"Configured Twitch settings: {json.dumps(twitch_config)}")
        return twitch_config
    
    @staticmethod
    def _configure_analytics(config: ServerConfiguration, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Configure analytics based on settings"""
        analytics_config = {
            'enable_command_tracking': settings.get('enableCommandTracking', True),
            'enable_user_stats': settings.get('enableUserStats', True),
            'enable_activity_reports': settings.get('enableActivityReports', True),
            'report_frequency': settings.get('reportFrequency', 'weekly'),
            'enable_dashboard_access': settings.get('enableDashboardAccess', True),
        }
        
        logger.info(f"Configured analytics settings: {json.dumps(analytics_config)}")
        return analytics_config