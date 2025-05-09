"""
Socket.IO event handlers for real-time communication between web dashboard and Discord bot.
"""
import os
import json
from datetime import datetime
import logging
from flask import request, session
from flask_socketio import SocketIO, emit, join_room, leave_room

# Initialize Socket.IO
socketio = SocketIO()

# Event tracking
active_connections = 0
server_rooms = {}  # Map server IDs to connected clients

def init_app(app):
    """Initialize Socket.IO with the Flask app"""
    cors_allowed_origins = "*"  # For development; restrict this in production
    socketio.init_app(app, cors_allowed_origins=cors_allowed_origins)
    register_handlers()
    return socketio

def register_handlers():
    """Register all Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        global active_connections
        active_connections += 1
        logging.info(f"Client connected. Active connections: {active_connections}")
        # Send connection statistics to all clients
        emit('connection_stats', {'active_connections': active_connections}, broadcast=True)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        global active_connections
        if active_connections > 0:
            active_connections -= 1
        logging.info(f"Client disconnected. Active connections: {active_connections}")
        # Send updated connection statistics to all clients
        emit('connection_stats', {'active_connections': active_connections}, broadcast=True)
    
    @socketio.on('join_server')
    def handle_join_server(data):
        """
        Handle client joining a server's updates
        
        Args:
            data: Dictionary containing server_id
        """
        server_id = data.get('server_id')
        if not server_id:
            return
        
        # Create a room for this server if it doesn't exist
        if server_id not in server_rooms:
            server_rooms[server_id] = 0
        
        # Join the room
        join_room(server_id)
        server_rooms[server_id] += 1
        
        logging.info(f"Client joined server room {server_id}. Total clients: {server_rooms[server_id]}")
        
        # Notify the client they've joined successfully
        emit('joined_server', {
            'server_id': server_id,
            'status': 'success',
            'viewers': server_rooms[server_id]
        })
    
    @socketio.on('leave_server')
    def handle_leave_server(data):
        """
        Handle client leaving a server's updates
        
        Args:
            data: Dictionary containing server_id
        """
        server_id = data.get('server_id')
        if not server_id or server_id not in server_rooms:
            return
        
        # Leave the room
        leave_room(server_id)
        server_rooms[server_id] -= 1
        
        # Clean up if no clients are left
        if server_rooms[server_id] <= 0:
            server_rooms.pop(server_id, None)
            
        logging.info(f"Client left server room {server_id}")
    
    @socketio.on('bot_command')
    def handle_bot_command(data):
        """
        Process a command sent from the dashboard to the bot
        
        Args:
            data: Dictionary containing command details
        """
        server_id = data.get('server_id')
        command = data.get('command')
        user_id = data.get('user_id')
        
        if not all([server_id, command, user_id]):
            emit('command_response', {
                'status': 'error',
                'message': 'Missing required data'
            })
            return
        
        # In a real implementation, this would queue the command for the bot to execute
        # For now, we'll just echo it back
        
        logging.info(f"Command request from user {user_id} for server {server_id}: {command}")
        
        emit('command_response', {
            'status': 'received',
            'message': f'Command {command} sent to server {server_id}',
            'timestamp': datetime.now().isoformat()
        })

# Functions to broadcast events from the Discord bot to the web dashboard

def broadcast_discord_event(event_type, server_id, data):
    """
    Broadcast a Discord event to all clients viewing a specific server
    
    Args:
        event_type: Type of event (message, join, leave, etc.)
        server_id: Discord server ID
        data: Event data to broadcast
    """
    event_data = {
        'type': event_type,
        'server_id': server_id,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    socketio.emit('discord_event', event_data, room=server_id)
    logging.info(f"Broadcast {event_type} event to server {server_id}")

def broadcast_server_stats(server_id, stats):
    """
    Broadcast updated server statistics
    
    Args:
        server_id: Discord server ID
        stats: Dictionary of server statistics
    """
    socketio.emit('server_stats_update', {
        'server_id': server_id,
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    }, room=server_id)

def broadcast_user_join(server_id, user_data):
    """Broadcast user join event to a server room"""
    broadcast_discord_event('user_join', server_id, user_data)

def broadcast_user_leave(server_id, user_data):
    """Broadcast user leave event to a server room"""
    broadcast_discord_event('user_leave', server_id, user_data)

def broadcast_message(server_id, message_data):
    """Broadcast message event to a server room"""
    broadcast_discord_event('message', server_id, message_data)

def broadcast_command_execution(server_id, command_data):
    """Broadcast command execution event to a server room"""
    broadcast_discord_event('command', server_id, command_data)

def broadcast_global_announcement(message, level='info'):
    """
    Broadcast a global announcement to all connected clients
    
    Args:
        message: Announcement message
        level: Importance level (info, warning, error)
    """
    socketio.emit('global_announcement', {
        'message': message,
        'level': level,
        'timestamp': datetime.now().isoformat()
    })
    logging.info(f"Global announcement sent: {message}")