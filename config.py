import os

# Bot configuration
BOT_CONFIG = {
    # Command prefix for the bot
    'prefix': os.getenv('BOT_PREFIX', '!'),
    
    # Bot description
    'description': 'A simple Discord bot with basic command handling',
    
    # Enable/disable message logging (for debugging purposes)
    'log_messages': os.getenv('LOG_MESSAGES', 'False').lower() == 'true',
    
    # Bot owner ID (for admin commands if needed)
    'owner_id': os.getenv('BOT_OWNER_ID', None),
    
    # Default embed color (hex color code)
    'embed_color': int(os.getenv('EMBED_COLOR', '0x00ff00'), 16),
}

# Convert owner_id to int if provided
if BOT_CONFIG['owner_id']:
    try:
        BOT_CONFIG['owner_id'] = int(BOT_CONFIG['owner_id'])
    except ValueError:
        BOT_CONFIG['owner_id'] = None

# Command cooldown settings (in seconds)
COOLDOWN_CONFIG = {
    'default_cooldown': 3,
    'ping_cooldown': 5,
    'info_cooldown': 10,
}

# Verification system configuration
VERIFICATION_CONFIG = {
    # Default verification settings per guild
    'default_verify_emoji': '✅',
    'default_verify_message': 'React with ✅ to verify and gain access to the server!',
    'welcome_message_enabled': True,
    'welcome_message': 'Welcome {user} to {server}! Please check the verification channel to get started.',
}

# In-memory storage for verification settings per guild
# In production, this should be stored in a database
VERIFICATION_DATA = {}

def get_verification_settings(guild_id):
    """Get verification settings for a guild"""
    if guild_id not in VERIFICATION_DATA:
        VERIFICATION_DATA[guild_id] = {
            'enabled': False,
            'channel_id': None,
            'message_id': None,
            'role_id': None,
            'emoji': VERIFICATION_CONFIG['default_verify_emoji'],
            'verify_message': VERIFICATION_CONFIG['default_verify_message'],
            'welcome_channel_id': None,
        }
    return VERIFICATION_DATA[guild_id]

def update_verification_settings(guild_id, **kwargs):
    """Update verification settings for a guild"""
    settings = get_verification_settings(guild_id)
    settings.update(kwargs)
    return settings

# Game role selection configuration
GAME_ROLE_CONFIG = {
    'default_games': {
        '🎮': 'Gamer',
        '⚔️': 'MMORPG Player', 
        '🔫': 'FPS Player',
        '🏎️': 'Racing Games',
        '🏀': 'Sports Games',
        '🧩': 'Puzzle Games',
        '📱': 'Mobile Gamer',
        '💻': 'PC Gamer',
        '🎯': 'Strategy Games',
        '👾': 'Retro Gamer'
    },
    'max_selections': 5,
    'embed_title': '🎮 Choose Your Game Roles!',
    'embed_description': 'React with the games you play to get the corresponding roles!',
}

# In-memory storage for game role settings per guild  
GAME_ROLE_DATA = {}

def get_game_role_settings(guild_id):
    """Get game role settings for a guild"""
    if guild_id not in GAME_ROLE_DATA:
        GAME_ROLE_DATA[guild_id] = {
            'enabled': False,
            'channel_id': None,
            'message_id': None,
            'game_roles': {},  # emoji -> role_id mapping
            'max_selections': GAME_ROLE_CONFIG['max_selections'],
        }
    return GAME_ROLE_DATA[guild_id]

def update_game_role_settings(guild_id, **kwargs):
    """Update game role settings for a guild"""
    settings = get_game_role_settings(guild_id)
    settings.update(kwargs)
    return settings

def add_game_role(guild_id, emoji, role_id):
    """Add a game role mapping"""
    settings = get_game_role_settings(guild_id)
    settings['game_roles'][emoji] = role_id
    return settings

def remove_game_role(guild_id, emoji):
    """Remove a game role mapping"""
    settings = get_game_role_settings(guild_id)
    if emoji in settings['game_roles']:
        del settings['game_roles'][emoji]
    return settings
