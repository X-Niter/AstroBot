import discord
from discord import app_commands
from discord.ext import commands
import logging

from services.openai_service import generate_response as openai_generate
from services.mongo_service import (
    add_mod_review,
    get_mod_reviews,
    get_mod_suggestions,
    add_mod_suggestion
)
from utils.embed_creator import create_mod_embed
from utils.error_handler import handle_command_error

logger = logging.getLogger(__name__)

class CommunityCommands(commands.Cog):
    """Commands for community features and mod reviews"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="review", description="Submit a review for a Minecraft mod")
    @app_commands.describe(
        mod_name="Name of the mod you're reviewing",
        rating="Your rating (1-5 stars)",
        review_text="Your review of the mod"
    )
    async def review(
        self, 
        interaction: discord.Interaction, 
        mod_name: str, 
        rating: int, 
        review_text: str
    ):
        """Submit a review for a Minecraft mod"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Validate the rating
            if rating < 1 or rating > 5:
                await interaction.followup.send(
                    "Rating must be between 1 and 5 stars.",
                    ephemeral=True
                )
                return
            
            # Add the review to MongoDB
            result = await add_mod_review(
                discord_id=str(interaction.user.id),
                discord_name=interaction.user.display_name,
                mod_name=mod_name,
                rating=rating,
                review_text=review_text
            )
            
            if result["success"]:
                # Create stars string (★☆)
                stars = "★" * rating + "☆" * (5 - rating)
                
                embed = create_mod_embed(
                    title=f"Mod Review: {mod_name}",
                    description=f"Thank you for submitting your review!"
                )
                
                embed.add_field(name="Rating", value=stars, inline=False)
                embed.add_field(name="Review", value=review_text, inline=False)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    f"Failed to submit review: {result['message']}",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"Error in /review command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="find", description="Find reviews for a Minecraft mod")
    @app_commands.describe(
        mod_name="Name of the mod to search for"
    )
    async def find(self, interaction: discord.Interaction, mod_name: str):
        """Find reviews for a Minecraft mod"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Get reviews from MongoDB
            reviews = await get_mod_reviews(mod_name)
            
            if reviews and len(reviews) > 0:
                # Calculate average rating
                avg_rating = sum(review["rating"] for review in reviews) / len(reviews)
                avg_stars = "★" * round(avg_rating) + "☆" * (5 - round(avg_rating))
                
                embed = create_mod_embed(
                    title=f"Mod Reviews: {mod_name}",
                    description=f"Found {len(reviews)} community reviews"
                )
                
                embed.add_field(
                    name="Average Rating",
                    value=f"{avg_stars} ({avg_rating:.1f}/5)",
                    inline=False
                )
                
                # Add the most recent reviews (limit to 3)
                for i, review in enumerate(reviews[:3]):
                    stars = "★" * review["rating"] + "☆" * (5 - review["rating"])
                    embed.add_field(
                        name=f"Review by {review['discord_name']}",
                        value=f"{stars}\n{review['review_text']}",
                        inline=False
                    )
                
                # Add a note if there are more reviews
                if len(reviews) > 3:
                    embed.set_footer(text=f"Showing 3 of {len(reviews)} reviews")
                
                await interaction.followup.send(embed=embed)
            else:
                embed = create_mod_embed(
                    title=f"No Reviews Found",
                    description=f"No community reviews found for '{mod_name}'."
                )
                embed.add_field(
                    name="Be the First!",
                    value="Use `/review` to submit the first review for this mod.",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /find command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="suggest", description="Suggest a new Minecraft mod idea")
    @app_commands.describe(
        title="A short title for your mod idea",
        description="Detailed description of your mod idea"
    )
    async def suggest(self, interaction: discord.Interaction, title: str, description: str):
        """Suggest a new Minecraft mod idea"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Get AI feedback on the idea
            prompt = (
                f"The following is a Minecraft mod idea. Please provide brief, constructive feedback "
                f"on the idea's originality, potential gameplay impact, and technical feasibility. "
                f"Be encouraging but honest. Keep your response under 200 words.\n\n"
                f"Mod Idea: {title}\n\n{description}"
            )
            
            ai_feedback = await openai_generate(prompt)
            
            # Add the suggestion to MongoDB
            result = await add_mod_suggestion(
                discord_id=str(interaction.user.id),
                discord_name=interaction.user.display_name,
                title=title,
                description=description,
                ai_feedback=ai_feedback
            )
            
            if result["success"]:
                embed = create_mod_embed(
                    title=f"Mod Suggestion: {title}",
                    description="Your mod idea has been submitted to the community suggestions database!"
                )
                
                embed.add_field(name="Description", value=description, inline=False)
                embed.add_field(name="AI Feedback", value=ai_feedback, inline=False)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    f"Failed to submit suggestion: {result['message']}",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"Error in /suggest command: {str(e)}")
            await handle_command_error(interaction, e)
    
    @app_commands.command(name="browse", description="Browse recent mod suggestions")
    @app_commands.describe(
        limit="Number of suggestions to show (default: 3, max: 5)"
    )
    async def browse(self, interaction: discord.Interaction, limit: int = 3):
        """Browse recent mod suggestions"""
        await interaction.response.defer(thinking=True)
        
        try:
            # Limit the number of suggestions
            if limit > 5:
                limit = 5
            
            # Get suggestions from MongoDB
            suggestions = await get_mod_suggestions(limit)
            
            if suggestions and len(suggestions) > 0:
                embed = create_mod_embed(
                    title="Recent Mod Suggestions",
                    description=f"Here are the {len(suggestions)} most recent community mod suggestions:"
                )
                
                for i, suggestion in enumerate(suggestions):
                    embed.add_field(
                        name=f"{i+1}. {suggestion['title']} (by {suggestion['discord_name']})",
                        value=f"{suggestion['description'][:150]}{'...' if len(suggestion['description']) > 150 else ''}",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
            else:
                embed = create_mod_embed(
                    title="No Suggestions Found",
                    description="No community mod suggestions found in the database."
                )
                embed.add_field(
                    name="Be the First!",
                    value="Use `/suggest` to submit the first mod idea!",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in /browse command: {str(e)}")
            await handle_command_error(interaction, e)
