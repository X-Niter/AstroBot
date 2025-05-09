import discord
from discord import app_commands
from discord.ext import commands
import logging

from services.openai_service import generate_response as openai_generate
from services.anthropic_service import generate_response as claude_generate
from utils.embed_creator import create_ai_response_embed
from utils.permissions import check_user_permissions
from utils.error_handler import handle_command_error

logger = logging.getLogger(__name__)

class AICommands(commands.Cog):
    """Commands for AI-powered assistance"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ask", description="Ask the AI assistant a question")
    @app_commands.describe(
        question="The question you want to ask",
        model="AI model to use (gpt or claude, defaults to gpt)"
    )
    async def ask(self, interaction: discord.Interaction, question: str, model: str = "gpt"):
        """Ask a general question to the AI assistant"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Choose the model based on user input
            if model.lower() in ["claude", "anthropic"]:
                response = await claude_generate(question)
                model_name = "Claude 3.5"
            else:
                response = await openai_generate(question)
                model_name = "GPT-4o"
            
            # Create and send the embed
            embed = create_ai_response_embed(
                title="AI Assistant Response",
                description=response,
                model_name=model_name,
                query=question
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /ask command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="fix", description="Fix code or troubleshoot Minecraft mod issues")
    @app_commands.describe(
        code="The code or error message you want to fix",
        context="Additional context about the issue (optional)",
        model="AI model to use (gpt or claude, defaults to gpt)"
    )
    async def fix(self, interaction: discord.Interaction, code: str, context: str = None, model: str = "gpt"):
        """Fix code or troubleshoot Minecraft mod issues"""
        await interaction.response.defer(thinking=True)
        
        try:
            prompt = f"Please help fix the following code or error:\n\n```\n{code}\n```"
            if context:
                prompt += f"\n\nAdditional context: {context}"
            
            # Choose the model based on user input
            if model.lower() in ["claude", "anthropic"]:
                response = await claude_generate(prompt)
                model_name = "Claude 3.5"
            else:
                response = await openai_generate(prompt)
                model_name = "GPT-4o"
            
            # Create and send the embed
            embed = create_ai_response_embed(
                title="Code Fix Suggestion",
                description=response,
                model_name=model_name,
                query=prompt
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /fix command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="idea", description="Generate a Minecraft mod idea")
    @app_commands.describe(
        theme="The theme or concept for the mod idea",
        complexity="The complexity level (simple, moderate, complex)",
        model="AI model to use (gpt or claude, defaults to gpt)"
    )
    async def idea(
        self, 
        interaction: discord.Interaction, 
        theme: str, 
        complexity: str = "moderate", 
        model: str = "gpt"
    ):
        """Generate a Minecraft mod idea based on a theme"""
        await interaction.response.defer(thinking=True)
        
        try:
            prompt = (
                f"Generate a detailed Minecraft mod idea based on the theme: '{theme}'. "
                f"Complexity level: {complexity}. "
                f"Include: concept description, core features, technical requirements, "
                f"possible implementation challenges, and how it would enhance gameplay."
            )
            
            # Choose the model based on user input
            if model.lower() in ["claude", "anthropic"]:
                response = await claude_generate(prompt)
                model_name = "Claude 3.5"
            else:
                response = await openai_generate(prompt)
                model_name = "GPT-4o"
            
            # Create and send the embed
            embed = create_ai_response_embed(
                title=f"Minecraft Mod Idea: {theme.capitalize()}",
                description=response,
                model_name=model_name,
                query=prompt
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /idea command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="tutorial", description="Generate a Minecraft modding tutorial")
    @app_commands.describe(
        topic="The modding topic you want to learn about",
        experience="Your experience level (beginner, intermediate, advanced)",
        model="AI model to use (gpt or claude, defaults to gpt)"
    )
    async def tutorial(
        self, 
        interaction: discord.Interaction, 
        topic: str, 
        experience: str = "beginner", 
        model: str = "gpt"
    ):
        """Generate a Minecraft modding tutorial on a specific topic"""
        await interaction.response.defer(thinking=True)
        
        try:
            prompt = (
                f"Create a Minecraft modding tutorial about '{topic}' for someone with {experience} experience. "
                f"Include: prerequisites, step-by-step instructions, code examples where relevant, "
                f"and common pitfalls to avoid."
            )
            
            # Choose the model based on user input
            if model.lower() in ["claude", "anthropic"]:
                response = await claude_generate(prompt)
                model_name = "Claude 3.5"
            else:
                response = await openai_generate(prompt)
                model_name = "GPT-4o"
            
            # Create and send the embed
            embed = create_ai_response_embed(
                title=f"Minecraft Modding Tutorial: {topic}",
                description=response,
                model_name=model_name,
                query=prompt
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /tutorial command: {str(e)}")
            await handle_command_error(interaction, e)
