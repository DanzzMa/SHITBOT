# Discord Bot

## Overview

This is a comprehensive Discord bot built with discord.py that provides basic command functionality, custom embed creation, and automated verification system for new members. The bot features a modular architecture with separate configuration management, command handling, verification system, and logging systems.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py Library**: Uses the discord.py library with the commands extension for structured command handling
- **Command System**: Implements a prefix-based command system with built-in help functionality
- **Event Handling**: Handles Discord events like bot ready, guild join/leave, and command errors

### Configuration Management
- **Environment-based Config**: Uses environment variables for sensitive data like bot tokens and owner IDs
- **Centralized Settings**: All bot configuration is managed through a dedicated config module
- **Cooldown System**: Implements per-command cooldown rates to prevent spam

### Command Architecture
- **Modular Command Setup**: Commands are defined in a separate module and dynamically loaded
- **Embed Responses**: Uses Discord embeds for rich, formatted command responses
- **Rate Limiting**: Built-in cooldown decorators prevent command abuse
- **Error Handling**: Global error handling for command failures and rate limiting

### Logging System
- **Multi-handler Logging**: Logs to both file (bot.log) and console
- **Structured Logging**: Uses Python's logging module with timestamps and log levels
- **Event Tracking**: Logs bot events, command usage, and errors for monitoring

### Verification System  
- **Reaction Role Verification**: Automated member verification using reaction roles
- **Welcome Messages**: Configurable welcome messages for new members
- **Member Join Events**: Tracks and responds to new member joins
- **Admin Controls**: Full administrative control over verification settings

### Game Role Selection System
- **Multi-Game Support**: Members can select roles for games they play
- **Reaction-Based Selection**: Easy role assignment/removal through emoji reactions
- **Configurable Limits**: Admins can set maximum number of game roles per member
- **Dynamic Role Management**: Add/remove game roles without system restart
- **Smart Limits**: Prevents role spam with automatic limit enforcement

### Bot Permissions
- **Message Content Intent**: Configured to read message content for command processing
- **Members Intent**: Enabled for member join/leave events and verification
- **Reactions Intent**: Enabled for reaction role verification system
- **Guild Monitoring**: Tracks guild joins/leaves for administrative purposes
- **Owner Privileges**: Supports bot owner identification for potential admin commands

## External Dependencies

### Core Dependencies
- **discord.py**: Primary Discord API wrapper library
- **psutil**: System monitoring for hardware/performance information
- **platform**: System information gathering

### Discord API Integration
- **Bot Token Authentication**: Requires Discord bot token for API access
- **Guild Permissions**: Needs appropriate permissions in Discord servers
- **Message Content Access**: Requires privileged intent for reading messages

### Environment Variables
- **BOT_TOKEN**: Discord bot authentication token
- **BOT_PREFIX**: Command prefix (defaults to '!')
- **BOT_OWNER_ID**: Bot owner's Discord user ID
- **EMBED_COLOR**: Hex color code for embed styling
- **LOG_MESSAGES**: Boolean flag for message logging