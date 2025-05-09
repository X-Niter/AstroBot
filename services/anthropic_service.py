import os
import logging
import anthropic
import base64
from anthropic import AsyncAnthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

async def generate_response(prompt, system_prompt=None):
    """
    Generate a response using Anthropic's API
    
    Args:
        prompt (str): The prompt to send to the model
        system_prompt (str, optional): Custom system prompt to override the default
        
    Returns:
        str: The generated response text
    """
    try:
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        # do not change this unless explicitly requested by the user
        default_system_prompt = "You are AstroBot, a helpful assistant specializing in Minecraft modding and development. You provide clear, accurate information about Minecraft mechanics, modding frameworks like Forge and Fabric, and Java programming concepts. Your responses are technical yet accessible, and you always aim to be educational."
        
        message = await client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            system=system_prompt or default_system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        logger.error(f"Error generating Anthropic response: {str(e)}")
        raise Exception(f"Failed to generate AI response: {str(e)}")

async def analyze_image(image_data, prompt=None):
    """
    Analyze an image using Anthropic's API
    
    Args:
        image_data (bytes): Image data in bytes or base64 string
        prompt (str, optional): Additional prompt instructions
        
    Returns:
        str: The analysis of the image
    """
    try:
        # Check if image_data is already a base64 string
        if isinstance(image_data, str):
            base64_image = image_data
        else:
            # Convert bytes to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Default prompt if none provided
        if not prompt:
            prompt = "Analyze this Minecraft-related image. Describe its features, style, and potential use in a mod."
        
        # Create the message
        message = await client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            system="You are an expert in Minecraft modding and game design. Analyze images related to Minecraft with technical insight.",
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}}
                    ]
                }
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        logger.error(f"Error analyzing image with Anthropic: {str(e)}")
        raise Exception(f"Failed to analyze image: {str(e)}")

async def generate_java_code(description, code_type="block"):
    """
    Generate Java code for Minecraft mods using Anthropic
    
    Args:
        description (str): Description of what the code should do
        code_type (str): Type of code to generate (block, item, entity, etc.)
        
    Returns:
        str: Generated Java code
    """
    try:
        # Customize the system prompt for code generation
        system_prompt = """You are a Minecraft modding expert specializing in Forge and Fabric development. 
        Generate well-structured, functional Java code that follows best practices. 
        Include comments to explain complex sections and always use the latest Minecraft modding standards.
        Only provide the Java code with appropriate imports and comments."""
        
        # Construct a detailed prompt based on the code type
        if code_type == "block":
            prompt = f"Generate Java code for a Minecraft mod that adds a new block with these properties: {description}. Use the latest Forge API."
        elif code_type == "item":
            prompt = f"Generate Java code for a Minecraft mod that adds a new item with these properties: {description}. Use the latest Forge API."
        elif code_type == "entity":
            prompt = f"Generate Java code for a Minecraft mod that adds a new entity with these behaviors: {description}. Use the latest Forge API."
        else:
            prompt = f"Generate Java code for a Minecraft mod that implements: {description}. Use the latest Forge API."
        
        message = await client.messages.create(
            model=ANTHROPIC_MODEL,
            system=system_prompt,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        logger.error(f"Error generating Java code with Anthropic: {str(e)}")
        raise Exception(f"Failed to generate Java code: {str(e)}")
