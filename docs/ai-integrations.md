# AI Integrations

AstroBot leverages advanced AI models to provide powerful features for Discord communities. This guide explains how to use and configure these AI integrations.

## Available AI Models

AstroBot integrates with multiple AI providers to deliver a range of capabilities:

### OpenAI GPT-4o

GPT-4o is OpenAI's most advanced multimodal model, capable of processing both text and images.

**Key capabilities:**
- Natural language understanding and generation
- Code analysis and generation
- Image description and analysis
- Reasoning about complex problems

### Anthropic Claude 3.5

Claude 3.5 is Anthropic's most advanced AI assistant, known for its thoughtful, helpful responses.

**Key capabilities:**
- Extended context handling
- Nuanced content analysis
- Safe and aligned outputs
- Detailed reasoning

### ElevenLabs Voice AI

ElevenLabs provides state-of-the-art voice synthesis capabilities.

**Key capabilities:**
- Natural-sounding voice generation
- Multiple voice options and languages
- Real-time text-to-speech
- Emotion and tone control

## Configuration

These AI integrations require API keys to function. You'll need to obtain these keys from the respective services and configure them in AstroBot.

### Setting API Keys

API keys can be configured in several ways:

1. **Environment Variables** (recommended for production):
   ```
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ```

2. **Web Dashboard**:
   - Navigate to Settings > API Keys
   - Enter your API keys in the appropriate fields
   - Click Save to store them securely

3. **Configuration File**:
   ```yaml
   ai:
     openai:
       api_key: your_openai_key
       model: gpt-4o
     anthropic:
       api_key: your_anthropic_key
       model: claude-3.5-sonnet-20240716
     elevenlabs:
       api_key: your_elevenlabs_key
       voice_id: default
   ```

## Usage Examples

### Discord Commands

Users can interact with AI models through Discord commands:

```
!ask [question]             # Ask a general question (GPT-4o)
!explain [concept]          # Get a detailed explanation (Claude 3.5)
!code [task]                # Generate code for a task (GPT-4o)
!image [description]        # Generate an image (DALL-E 3)
!voiceover [text]           # Generate voice audio (ElevenLabs)
!analyze [image]            # Analyze an uploaded image (GPT-4o Vision)
```

### Code Examples

#### Using OpenAI in your custom commands:

```python
from services.ai_service import openai_client

async def generate_response(prompt):
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

@bot.command()
async def custom_ai(ctx, *, prompt):
    """Custom AI response using GPT-4o"""
    response = await generate_response(prompt)
    await ctx.send(response)
```

#### Using Claude in your custom commands:

```python
from services.ai_service import anthropic_client

async def generate_claude_response(prompt):
    response = await anthropic_client.messages.create(
        model="claude-3.5-sonnet-20240716",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

@bot.command()
async def deep_think(ctx, *, question):
    """Thoughtful response using Claude 3.5"""
    response = await generate_claude_response(question)
    await ctx.send(response)
```

## Managing Costs

AI API usage incurs costs, so AstroBot includes tools to help manage and monitor usage:

1. **Rate Limiting**: Configure per-user or per-server limits
2. **Usage Dashboard**: Monitor AI usage in the web dashboard
3. **Cost Estimation**: Get estimates before enabling AI features
4. **Tiered Access**: Restrict certain AI features to premium users

## Best Practices

1. **Prompt Engineering**: Craft clear, specific prompts for better results
2. **Context Management**: Provide sufficient context for complex questions
3. **Model Selection**: Use GPT-4o for general tasks, Claude 3.5 for nuanced reasoning
4. **Caching**: Enable response caching for common queries to reduce costs
5. **Safety Filters**: Keep AI safety filters enabled to prevent inappropriate content

## Troubleshooting

If you encounter issues with AI integrations:

1. **Verify API Keys**: Ensure your API keys are valid and have sufficient credits
2. **Check Logs**: Review logs for error messages
3. **Network Issues**: Confirm your server can reach the AI providers' APIs
4. **Model Availability**: Some models may have availability limitations
5. **Rate Limits**: You might be hitting rate limits from the AI providers

For persistent issues, check the AstroBot documentation for updates or contact support.