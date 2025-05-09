import os
import logging
import asyncio
from mctools import RCONClient

from config import (
    MINECRAFT_SERVER_IP,
    MINECRAFT_SERVER_PORT,
    MINECRAFT_RCON_PASSWORD
)

# Configure logging
logger = logging.getLogger(__name__)

async def _run_rcon_command(command):
    """
    Execute a command on the Minecraft server via RCON
    
    Args:
        command (str): The command to execute
        
    Returns:
        dict: Result of the operation
    """
    try:
        # Create an event loop for thread safety
        loop = asyncio.get_event_loop()
        
        # Run the RCON command in a separate thread to avoid blocking
        def run_command():
            try:
                with RCONClient(MINECRAFT_SERVER_IP, port=MINECRAFT_SERVER_PORT, password=MINECRAFT_RCON_PASSWORD) as client:
                    response = client.command(command)
                    return {"success": True, "response": response}
            except Exception as e:
                logger.error(f"RCON command error: {str(e)}")
                return {"success": False, "message": str(e)}
        
        # Execute the command in the thread pool
        result = await loop.run_in_executor(None, run_command)
        return result
    except Exception as e:
        logger.error(f"Error running RCON command: {str(e)}")
        return {"success": False, "message": str(e)}

async def get_server_status():
    """
    Get the current status of the Minecraft server
    
    Returns:
        dict: Server status information
    """
    try:
        # Try to connect to the server via RCON
        rcon_result = await _run_rcon_command("list")
        
        if rcon_result["success"]:
            response = rcon_result["response"]
            
            # Parse the player list response
            # Example: "There are 3/20 players online: player1, player2, player3"
            try:
                parts = response.split(":")
                players_part = parts[0].strip()
                
                # Extract numbers
                count_parts = players_part.split("players online")[0].strip()
                count_parts = count_parts.replace("There are ", "").strip()
                
                current, maximum = map(int, count_parts.split("/"))
                
                # Extract player names if any
                player_list = []
                if len(parts) > 1 and parts[1].strip():
                    player_list = [name.strip() for name in parts[1].split(",")]
                
                # Get server version
                version_result = await _run_rcon_command("version")
                version = "Unknown"
                if version_result["success"]:
                    version_lines = version_result["response"].split("\n")
                    if version_lines:
                        version = version_lines[0].split(":")[1].strip() if ":" in version_lines[0] else version_lines[0]
                
                return {
                    "online": True,
                    "players_online": current,
                    "max_players": maximum,
                    "player_list": player_list,
                    "version": version
                }
            except Exception as e:
                logger.error(f"Error parsing server status: {str(e)}")
                return {
                    "online": True,
                    "players_online": 0,
                    "max_players": 0,
                    "player_list": [],
                    "version": "Unknown"
                }
        else:
            return {
                "online": False,
                "players_online": 0,
                "max_players": 0,
                "player_list": [],
                "version": "Unknown"
            }
    except Exception as e:
        logger.error(f"Error getting server status: {str(e)}")
        return {
            "online": False,
            "players_online": 0,
            "max_players": 0,
            "player_list": [],
            "version": "Unknown"
        }

async def whitelist_player(username):
    """
    Add a player to the server whitelist
    
    Args:
        username (str): Minecraft username to add
        
    Returns:
        dict: Result of the operation
    """
    try:
        result = await _run_rcon_command(f"whitelist add {username}")
        
        if result["success"]:
            return {"success": True, "message": "Player added to whitelist"}
        else:
            return {"success": False, "message": result["message"]}
    except Exception as e:
        logger.error(f"Error adding player to whitelist: {str(e)}")
        return {"success": False, "message": str(e)}

async def remove_from_whitelist(username):
    """
    Remove a player from the server whitelist
    
    Args:
        username (str): Minecraft username to remove
        
    Returns:
        dict: Result of the operation
    """
    try:
        result = await _run_rcon_command(f"whitelist remove {username}")
        
        if result["success"]:
            return {"success": True, "message": "Player removed from whitelist"}
        else:
            return {"success": False, "message": result["message"]}
    except Exception as e:
        logger.error(f"Error removing player from whitelist: {str(e)}")
        return {"success": False, "message": str(e)}

async def execute_command(command):
    """
    Execute an arbitrary command on the Minecraft server
    
    Args:
        command (str): Command to execute (without the leading /)
        
    Returns:
        dict: Result of the operation
    """
    try:
        result = await _run_rcon_command(command)
        
        if result["success"]:
            return {"success": True, "response": result["response"]}
        else:
            return {"success": False, "message": result["message"]}
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return {"success": False, "message": str(e)}

async def restart_server():
    """
    Restart the Minecraft server
    
    Returns:
        dict: Result of the operation
    """
    try:
        # Send a warning to all players
        await _run_rcon_command("say SERVER RESTARTING IN 30 SECONDS!")
        await asyncio.sleep(20)
        await _run_rcon_command("say SERVER RESTARTING IN 10 SECONDS!")
        await asyncio.sleep(5)
        await _run_rcon_command("say SERVER RESTARTING IN 5 SECONDS!")
        await asyncio.sleep(5)
        
        # Stop the server (this will trigger a restart if set up properly)
        result = await _run_rcon_command("stop")
        
        if result["success"]:
            return {"success": True, "message": "Server restart initiated"}
        else:
            return {"success": False, "message": result["message"]}
    except Exception as e:
        logger.error(f"Error restarting server: {str(e)}")
        return {"success": False, "message": str(e)}
