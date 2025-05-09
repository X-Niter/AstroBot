# Troubleshooting Guide

This guide covers common issues you might encounter when working with AstroBot and how to resolve them.

## Common Errors

### Undefined Variables

If you encounter errors like `F821 undefined name 'func'` or `undefined name 'DiscordServer'`, it usually means that a necessary import is missing. Here's how to fix these common issues:

#### Missing SQLAlchemy Functions

```python
# Add this import at the top of your file
from sqlalchemy import func
```

The `func` object is used for SQL functions and aggregations. It's commonly needed in queries that use operations like `count()`, `max()`, or `min()`.

#### Missing Model References

If you see `undefined name 'DiscordServer'` or similar, you need to import the model:

```python
# Add this import at the top of your file
from models import DiscordServer
```

### Database Connection Issues

If you encounter database connectivity problems:

1. Check that your database URL is correctly set in the environment variables
2. Verify that the PostgreSQL service is running
3. Ensure that your models are properly defined with correct relationships

```python
# Debug database connection
print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
try:
    db.session.execute("SELECT 1")
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {str(e)}")
```

### Module Import Errors

If you see `ModuleNotFoundError` or `ImportError`:

1. Check your project structure to ensure the module exists
2. Verify that your Python path includes the necessary directories
3. Make sure all dependencies are installed

## Application Startup Issues

### Flask Application Not Starting

If the Flask application fails to start:

1. Check for syntax errors in your Python files
2. Look for circular imports
3. Verify that the port (5000) is not already in use

### Discord Bot Not Connecting

If the Discord bot fails to connect:

1. Verify that your `DISCORD_TOKEN` is correct and properly set
2. Check that your bot has the necessary permissions
3. Ensure that you've enabled the necessary Gateway Intents in the Discord Developer Portal

## Debugging Techniques

### Logging

AstroBot uses Python's built-in logging module. To add more detailed logs:

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use throughout your code
logger.debug("Detailed information for debugging")
logger.info("Confirmation that things are working")
logger.warning("Something unexpected happened")
logger.error("A more serious problem occurred")
logger.critical("A fatal error occurred")
```

### Interactive Debugging

You can use Python's built-in debugger (pdb):

```python
import pdb

# Add this line where you want to start debugging
pdb.set_trace()
```

When this line is executed, Python will stop and provide an interactive debug console.

## Getting Support

If you can't resolve the issue using this guide:

1. Check existing issues on GitHub to see if someone else has encountered the same problem
2. Create a new issue with a detailed description of the problem and the steps to reproduce it
3. Join our Discord server for community support