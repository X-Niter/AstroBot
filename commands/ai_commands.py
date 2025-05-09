import discord
from discord import app_commands
from discord.ext import commands
import logging

from services.openai_service import generate_response as openai_generate, generate_image, generate_java_code
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
            
    @app_commands.command(name="generate", description="Generate an image for a Minecraft mod concept")
    @app_commands.describe(
        description="Description of the image you want to generate",
        style="Style of the image (realistic, cartoon, pixelated, etc.)",
    )
    async def generate_mod_image(
        self,
        interaction: discord.Interaction,
        description: str,
        style: str = "pixelated"
    ):
        """Generate an image for a Minecraft mod concept using DALL-E"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Enhance the prompt with style information
            enhanced_prompt = f"{description}, {style} style"
            
            # Generate the image
            image_result = await generate_image(enhanced_prompt)
            
            # Create a rich embed for the response
            embed = discord.Embed(
                title="Generated Minecraft Concept Art",
                description=f"**Based on:** {description}\n**Style:** {style}",
                color=discord.Color.from_rgb(0, 208, 255)  # AI blue color
            )
            
            # Add the image URL to the embed
            embed.set_image(url=image_result["url"])
            
            # Add footer with AI model info
            embed.set_footer(text="Generated by DALL-E • Powered by AstroBot")
            
            # Send the embed with the image
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /generate command: {str(e)}")
            await handle_command_error(interaction, e)
            
    @app_commands.command(name="code", description="Generate Java code for a Minecraft mod")
    @app_commands.describe(
        description="Description of what the code should do",
        type="Type of code to generate (block, item, entity, other)"
    )
    async def generate_code(
        self,
        interaction: discord.Interaction,
        description: str,
        type: str = "block"
    ):
        """Generate Java code for a Minecraft mod"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Normalize the code type
            code_type = type.lower()
            if code_type not in ["block", "item", "entity"]:
                code_type = "other"
                
            # Generate the code
            code_result = await generate_java_code(description, code_type)
            
            # Create a rich embed for the response
            embed = discord.Embed(
                title=f"Generated Java Code: {type.capitalize()}",
                description=f"**Description:** {description}\n```java\n{code_result[:4000]}```",
                color=discord.Color.from_rgb(0, 208, 255)  # AI blue color
            )
            
            # If the code is too long, add a note
            if len(code_result) > 4000:
                embed.add_field(
                    name="Note",
                    value="The generated code has been truncated due to length. Consider breaking your request into smaller components.",
                    inline=False
                )
            
            # Add footer with AI model info
            embed.set_footer(text="Generated by GPT-4o • Powered by AstroBot")
            
            # Send the embed with the code
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /code command: {str(e)}")
            await handle_command_error(interaction, e)
