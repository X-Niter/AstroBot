import os
import json
import logging
import aiohttp
import base64
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_response(prompt, system_prompt=None):
    """
    Generate a response using OpenAI's API
    
    Args:
        prompt (str): The prompt to send to the model
        system_prompt (str, optional): Custom system prompt to override the default
        
    Returns:
        str: The generated response text
    """
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        default_system_prompt = "You are AstroBot, a helpful assistant specializing in Minecraft modding and development. You provide clear, accurate information about Minecraft mechanics, modding frameworks like Forge and Fabric, and Java programming concepts. Your responses are technical yet accessible, and you always aim to be educational."
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt or default_system_prompt},
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

async def analyze_image(image_data):
    """
    Analyze an image using OpenAI's API
    
    Args:
        image_data (bytes): Image data in bytes or base64 string
        
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
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this Minecraft-related image. Describe its features, style, and potential use in a mod."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise Exception(f"Failed to analyze image: {str(e)}")

async def generate_image(prompt):
    """
    Generate an image using DALL-E
    
    Args:
        prompt (str): Description of the image to generate
        
    Returns:
        dict: Dictionary containing image URL and other data
    """
    try:
        # Enhance the prompt for Minecraft-themed image
        minecraft_prompt = f"Minecraft-styled {prompt}. Pixelated, blocky, game art style."
        
        response = await client.images.generate(
            model="dall-e-3",
            prompt=minecraft_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url"
        )
        
        return {
            "url": response.data[0].url,
            "prompt": minecraft_prompt,
            "revised_prompt": response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else None
        }
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise Exception(f"Failed to generate image: {str(e)}")

async def generate_java_code(description, code_type="block"):
    """
    Generate Java code for Minecraft mods
    
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
        
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating Java code: {str(e)}")
        raise Exception(f"Failed to generate Java code: {str(e)}")
