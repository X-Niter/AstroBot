# API Reference

AstroBot provides a RESTful API for integrating with external services.

## Authentication

All API requests require authentication using an API key.

### Obtaining an API Key

1. Log in to the web dashboard
2. Go to Settings > API
3. Generate a new API key

### Using the API Key

Include the API key in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

## API Endpoints

### Bot Status

```
GET /api/status
```

Returns the current status of the bot.

### Minecraft Server

```
GET /api/minecraft/status
```

Returns the status of the Minecraft server.

```
GET /api/minecraft/players
```

Returns a list of online players.

### Twitch Integration

```
GET /api/twitch/status
```

Returns the status of the Twitch integration.

```
POST /api/twitch/notify
```

Toggle Twitch stream notifications.