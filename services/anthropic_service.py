import os
import logging
import anthropic
from anthropic import AsyncAnthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

async def generate_response(prompt):
    """
    Generate a response using Anthropic's API
    
    Args:
        prompt (str): The prompt to send to the model
        
    Returns:
        str: The generated response text
    """
    try:
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        # do not change this unless explicitly requested by the user
        message = await client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            system="You are AstroBot, a helpful assistant specializing in Minecraft modding and development. You provide clear, accurate information about Minecraft mechanics, modding frameworks like Forge and Fabric, and Java programming concepts. Your responses are technical yet accessible, and you always aim to be educational.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        logger.error(f"Error generating Anthropic response: {str(e)}")
        raise Exception(f"Failed to generate AI response: {str(e)}")
