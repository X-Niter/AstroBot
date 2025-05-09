import os
import json
import logging
import aiohttp
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_response(prompt):
    """
    Generate a response using OpenAI's API
    
    Args:
        prompt (str): The prompt to send to the model
        
    Returns:
        str: The generated response text
    """
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are AstroBot, a helpful assistant specializing in Minecraft modding and development. You provide clear, accurate information about Minecraft mechanics, modding frameworks like Forge and Fabric, and Java programming concepts. Your responses are technical yet accessible, and you always aim to be educational."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating OpenAI response: {str(e)}")
        raise Exception(f"Failed to generate AI response: {str(e)}")

async def generate_json_response(prompt, schema_description):
    """
    Generate a structured JSON response using OpenAI's API
    
    Args:
        prompt (str): The prompt to send to the model
        schema_description (str): Description of the JSON schema expected in the response
        
    Returns:
        dict: The generated response as a JSON object
    """
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"You are AstroBot, a helpful assistant that responds with structured JSON data. {schema_description}"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse the response as JSON
        response_text = response.choices[0].message.content
        return json.loads(response_text)
    except Exception as e:
        logger.error(f"Error generating OpenAI JSON response: {str(e)}")
        raise Exception(f"Failed to generate AI JSON response: {str(e)}")
