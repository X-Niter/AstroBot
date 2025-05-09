"""
AstroBot AI Service

Provides AI-powered functionality using OpenAI and Anthropic models.
"""
import os
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple

# Import AI models
from openai import OpenAI
from anthropic import Anthropic

# Setup logging
logger = logging.getLogger(__name__)

# Initialize AI clients
openai_client = None
anthropic_client = None

# Initialize API keys from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Initialize clients if API keys are available
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")

if ANTHROPIC_API_KEY:
    try:
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("Anthropic client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic client: {str(e)}")

# Configuration
DEFAULT_MODEL = "gpt-4o"  # the newest OpenAI model, released May 13, 2024
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # the newest Anthropic model, released October 22, 2024


async def analyze_context(
    messages: List[Dict[str, str]],
    channel_name: str,
    user_trust_score: float
) -> Dict[str, Any]:
    """
    Analyze conversation context to provide AI-powered moderation insights
    
    Args:
        messages: List of recent messages in the format {author: str, content: str, timestamp: str}
        channel_name: Name of the channel where the conversation is happening
        user_trust_score: Trust score of the user being evaluated (0.0 to 1.0)
        
    Returns:
        Dict containing analysis results including toxicity scores, intent detection, etc.
    """
    if not openai_client:
        logger.warning("OpenAI client not initialized, cannot analyze context")
        return {
            "error": "AI service not available",
            "toxicity_score": 0.0,
            "intent": "unknown",
            "recommendation": "manual_review"
        }
    
    try:
        # Format messages for analysis
        context = "\n".join([f"{msg['author']}: {msg['content']}" for msg in messages])
        
        # Create system prompt
        system_prompt = """You are an AI moderation assistant analyzing Discord conversations. 
        Analyze the following conversation and provide:
        1. A toxicity score from 0.0 to 1.0
        2. The likely intent of the latest message
        3. A moderation recommendation (allow, flag, remove)
        4. A brief explanation
        
        Format your response as JSON.
        """
        
        # Get analysis from OpenAI
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Channel: {channel_name}\nUser Trust Score: {user_trust_score}\n\nConversation:\n{context}"}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        # Add metadata
        result["model_used"] = DEFAULT_MODEL
        result["channel"] = channel_name
        result["user_trust_score"] = user_trust_score
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing context: {str(e)}")
        return {
            "error": str(e),
            "toxicity_score": 0.0,
            "intent": "unknown",
            "recommendation": "manual_review"
        }


async def detect_toxic_content(content: str) -> bool:
    """
    Detect if content is toxic or violates community guidelines
    
    Args:
        content: The content to analyze
        
    Returns:
        bool: Whether the content is toxic
    """
    if not openai_client:
        logger.warning("OpenAI client not initialized, cannot detect toxic content")
        return False
    
    try:
        # Create system prompt
        system_prompt = """You are a content moderator. 
        Analyze the following content and determine if it violates community guidelines.
        Consider: hate speech, harassment, threats, explicit content, spam, or other harmful content.
        Return true if toxic, false if safe."""
        
        # Get analysis from OpenAI
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.1  # Low temperature for more deterministic results
        )
        
        result = response.choices[0].message.content.strip().lower()
        return "true" in result
        
    except Exception as e:
        logger.error(f"Error detecting toxic content: {str(e)}")
        return False


async def generate_command_suggestion(description: str) -> Optional[Dict[str, str]]:
    """
    Generate a custom command suggestion based on user description
    
    Args:
        description: User's description of what they want the command to do
        
    Returns:
        Dict with command details (trigger, response, etc.) or None if generation failed
    """
    if not openai_client:
        logger.warning("OpenAI client not initialized, cannot generate command suggestion")
        return None
    
    try:
        # Create system prompt
        system_prompt = """You are an expert Discord bot command creator.
        Based on the user's description, create a custom command with:
        1. A trigger word/phrase
        2. Command trigger type (exact, startswith, contains, regex)
        3. Response type (text, embed, reaction, dm, file, complex)
        4. Command content/response
        5. Usage instructions
        
        Format your response as JSON with these fields: 
        {
            "trigger": string,
            "trigger_type": string,
            "response_type": string,
            "content": string,
            "usage": string
        }
        """
        
        # Get suggestion from OpenAI
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a command that: {description}"}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"Error generating command suggestion: {str(e)}")
        return None


async def suggest_embed_design(description: str) -> Optional[Dict[str, Any]]:
    """
    Generate an embed design based on user description
    
    Args:
        description: User's description of what they want the embed to look like
        
    Returns:
        Dict with embed details or None if generation failed
    """
    if not openai_client:
        logger.warning("OpenAI client not initialized, cannot suggest embed design")
        return None
    
    try:
        # Create system prompt
        system_prompt = """You are an expert Discord embed designer.
        Based on the user's description, create a Discord embed with:
        1. Title
        2. Description
        3. Fields
        4. Color (hex code)
        5. Author info
        6. Footer text
        
        Format your response as JSON that can be directly used with discord.py.
        """
        
        # Get suggestion from OpenAI
        response = openai_client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create an embed that: {description}"}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse response
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"Error suggesting embed design: {str(e)}")
        return None


async def analyze_user_message(content: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze a user message for sentiment, intent, and key topics
    
    Args:
        content: The message content to analyze
        context: Optional list of previous messages for context
        
    Returns:
        Dict with analysis results
    """
    if not anthropic_client:
        logger.warning("Anthropic client not initialized, falling back to OpenAI")
        if not openai_client:
            logger.warning("OpenAI client not initialized, cannot analyze user message")
            return {
                "error": "AI service not available",
                "sentiment": "neutral",
                "intent": "unknown",
                "topics": []
            }
    
    try:
        if anthropic_client:
            # Using Claude for this task
            system_prompt = """Analyze this message and provide:
            1. Sentiment (positive, negative, neutral)
            2. User's likely intent
            3. Key topics mentioned
            4. Any questions needing answers
            
            Format your response as JSON.
            """
            
            # Format context if provided
            context_text = ""
            if context:
                context_text = "Previous messages for context:\n" + "\n".join(context) + "\n\nCurrent message to analyze:\n"
            
            # Get analysis from Anthropic
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"{context_text}{content}"}
                ],
                temperature=0.1
            )
            
            # Parse response 
            result = json.loads(response.content[0].text)
            result["model_used"] = CLAUDE_MODEL
            
        else:
            # Fallback to OpenAI
            system_prompt = """Analyze this message and provide:
            1. Sentiment (positive, negative, neutral)
            2. User's likely intent
            3. Key topics mentioned
            4. Any questions needing answers
            
            Format your response as JSON.
            """
            
            # Format context if provided
            context_text = ""
            if context:
                context_text = "Previous messages for context:\n" + "\n".join(context) + "\n\nCurrent message to analyze:\n"
            
            # Get analysis from OpenAI
            response = openai_client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context_text}{content}"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            result["model_used"] = DEFAULT_MODEL
            
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing user message: {str(e)}")
        return {
            "error": str(e),
            "sentiment": "neutral",
            "intent": "unknown",
            "topics": []
        }


async def is_available() -> Tuple[bool, str]:
    """
    Check if AI services are available
    
    Returns:
        Tuple[bool, str]: Availability status and message
    """
    if openai_client or anthropic_client:
        services = []
        if openai_client:
            services.append("OpenAI")
        if anthropic_client:
            services.append("Anthropic")
        return True, f"AI services available: {', '.join(services)}"
    else:
        return False, "No AI services configured. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to enable AI features."