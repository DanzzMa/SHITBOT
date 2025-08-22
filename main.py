import discord
from discord.ext import commands
import os
import logging
from config import BOT_CONFIG, VERIFICATION_CONFIG, get_verification_settings, get_game_role_settings
from commands import setup_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bot')

# Configure intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=BOT_CONFIG['prefix'],
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guild(s)')
        
        # Set bot activity status
        activity = discord.Game(name=f"{BOT_CONFIG['prefix']}help")
        await self.change_presence(activity=activity)
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild"""
        logger.info(f'Bot joined guild: {guild.name} (id: {guild.id})')
    
    async def on_guild_remove(self, guild):
        """Called when the bot leaves a guild"""
        logger.info(f'Bot left guild: {guild.name} (id: {guild.id})')
    
    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"❌ Command not found. Use `{BOT_CONFIG['prefix']}help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument. Use `{BOT_CONFIG['prefix']}help {ctx.command}` for usage info.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command on cooldown. Try again in {error.retry_after:.2f} seconds.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command.")
        else:
            logger.error(f'Unhandled error in command {ctx.command}: {error}')
            await ctx.send("❌ An unexpected error occurred. Please try again later.")
    
    async def on_member_join(self, member):
        """Called when a new member joins the server"""
        guild_id = member.guild.id
        settings = get_verification_settings(guild_id)
        
        logger.info(f'New member joined: {member} in {member.guild.name}')
        
        # Send welcome message if enabled and channel is set
        if VERIFICATION_CONFIG['welcome_message_enabled'] and settings.get('welcome_channel_id'):
            try:
                welcome_channel = member.guild.get_channel(settings['welcome_channel_id'])
                if welcome_channel:
                    welcome_text = VERIFICATION_CONFIG['welcome_message'].format(
                        user=member.mention,
                        server=member.guild.name
                    )
                    
                    welcome_embed = discord.Embed(
                        title="👋 Welcome!",
                        description=welcome_text,
                        color=BOT_CONFIG['embed_color']
                    )
                    
                    if settings['enabled'] and settings['channel_id']:
                        verify_channel = member.guild.get_channel(settings['channel_id'])
                        if verify_channel:
                            welcome_embed.add_field(
                                name="🔐 Verification Required",
                                value=f"Please head to {verify_channel.mention} to verify and gain access to the server!",
                                inline=False
                            )
                    
                    welcome_embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                    await welcome_channel.send(embed=welcome_embed)
                    
            except Exception as e:
                logger.error(f'Error sending welcome message: {e}')
    
    async def on_raw_reaction_add(self, payload):
        """Called when a reaction is added to any message"""
        # Ignore bot reactions
        if payload.user_id == self.user.id:
            return
        
        guild = self.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # Check verification system
        verification_settings = get_verification_settings(guild.id)
        
        # Check if this is a verification reaction
        if (verification_settings['enabled'] and 
            payload.message_id == verification_settings['message_id'] and 
            str(payload.emoji) == verification_settings['emoji']):
            
            try:
                role = guild.get_role(verification_settings['role_id'])
                
                if role and role not in member.roles:
                    await member.add_roles(role, reason="Verified through reaction role")
                    logger.info(f'Verified user: {member} in {guild.name}')
                    
                    # Send DM confirmation (optional)
                    try:
                        dm_embed = discord.Embed(
                            title="✅ Verification Successful!",
                            description=f"You have been verified in **{guild.name}**! You now have access to the server.",
                            color=0x00ff00
                        )
                        await member.send(embed=dm_embed)
                    except discord.Forbidden:
                        # User has DMs disabled, that's fine
                        pass
                        
            except Exception as e:
                logger.error(f'Error in verification reaction: {e}')
                
        # Check game role system
        game_settings = get_game_role_settings(guild.id)
        
        # Check if this is a game role reaction
        if (game_settings['enabled'] and 
            payload.message_id == game_settings['message_id'] and 
            str(payload.emoji) in game_settings['game_roles']):
            
            try:
                role_id = game_settings['game_roles'][str(payload.emoji)]
                role = guild.get_role(role_id)
                
                if role and role not in member.roles:
                    # Check if member has reached max selections
                    current_game_roles = []
                    for emoji, check_role_id in game_settings['game_roles'].items():
                        check_role = guild.get_role(check_role_id)
                        if check_role and check_role in member.roles:
                            current_game_roles.append(check_role)
                    
                    max_selections = game_settings.get('max_selections', 5)
                    if len(current_game_roles) >= max_selections:
                        # Remove reaction and notify user
                        try:
                            channel = guild.get_channel(payload.channel_id)
                            message = await channel.fetch_message(payload.message_id)
                            await message.remove_reaction(payload.emoji, member)
                            
                            # Send DM about limit
                            try:
                                limit_embed = discord.Embed(
                                    title="⚠️ Selection Limit Reached",
                                    description=f"You can only have {max_selections} game roles maximum in **{guild.name}**!\nRemove some roles first before adding new ones.",
                                    color=0xff9900
                                )
                                await member.send(embed=limit_embed)
                            except discord.Forbidden:
                                pass
                                
                        except Exception:
                            pass
                        return
                    
                    # Add the game role
                    await member.add_roles(role, reason="Game role selected through reaction")
                    logger.info(f'Game role {role.name} added to {member} in {guild.name}')
                    
                    # Send DM confirmation (optional)
                    try:
                        dm_embed = discord.Embed(
                            title="🎮 Game Role Added!",
                            description=f"You now have the **{role.name}** role in **{guild.name}**!",
                            color=0x00ff00
                        )
                        await member.send(embed=dm_embed)
                    except discord.Forbidden:
                        # User has DMs disabled, that's fine
                        pass
                        
            except Exception as e:
                logger.error(f'Error in game role reaction: {e}')
    
    async def on_raw_reaction_remove(self, payload):
        """Called when a reaction is removed from any message"""
        # Ignore bot reactions
        if payload.user_id == self.user.id:
            return
        
        guild = self.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        # Check verification system
        verification_settings = get_verification_settings(guild.id)
        
        # Check if this is a verification reaction removal
        if (verification_settings['enabled'] and 
            payload.message_id == verification_settings['message_id'] and 
            str(payload.emoji) == verification_settings['emoji']):
            
            try:
                role = guild.get_role(verification_settings['role_id'])
                
                if role and role in member.roles:
                    await member.remove_roles(role, reason="Verification reaction removed")
                    logger.info(f'Removed verification from user: {member} in {guild.name}')
                    
                    # Send DM notification (optional)
                    try:
                        dm_embed = discord.Embed(
                            title="⚠️ Verification Removed",
                            description=f"Your verification in **{guild.name}** has been removed. React again to regain access.",
                            color=0xff9900
                        )
                        await member.send(embed=dm_embed)
                    except discord.Forbidden:
                        # User has DMs disabled, that's fine
                        pass
                        
            except Exception as e:
                logger.error(f'Error in verification reaction removal: {e}')
                
        # Check game role system
        game_settings = get_game_role_settings(guild.id)
        
        # Check if this is a game role reaction removal
        if (game_settings['enabled'] and 
            payload.message_id == game_settings['message_id'] and 
            str(payload.emoji) in game_settings['game_roles']):
            
            try:
                role_id = game_settings['game_roles'][str(payload.emoji)]
                role = guild.get_role(role_id)
                
                if role and role in member.roles:
                    await member.remove_roles(role, reason="Game role deselected through reaction removal")
                    logger.info(f'Game role {role.name} removed from {member} in {guild.name}')
                    
                    # Send DM confirmation (optional)
                    try:
                        dm_embed = discord.Embed(
                            title="🎮 Game Role Removed",
                            description=f"The **{role.name}** role has been removed from your profile in **{guild.name}**.",
                            color=0xff9900
                        )
                        await member.send(embed=dm_embed)
                    except discord.Forbidden:
                        # User has DMs disabled, that's fine
                        pass
                        
            except Exception as e:
                logger.error(f'Error in game role reaction removal: {e}')
    
    async def on_message(self, message):
        """Called for every message the bot can see"""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        
        # Log message activity (optional, can be disabled for privacy)
        if BOT_CONFIG.get('log_messages', False):
            logger.debug(f'Message from {message.author}: {message.content}')
        
        # Process commands
        await self.process_commands(message)

async def main():
    """Main function to start the bot"""
    # Get Discord token from environment variable
    token = MTQwODA3NjkyMTU5NzU5MTY5Mg.GRfVJq.O4M8lRXmn5sL-PveUCIfReKYy_yWEuUoxktuac
    
    if not token:
        logger.error('DISCORD_TOKEN not found in environment variables!')
        logger.error('Please set your Discord bot token in the environment or .env file')
        return
    
    # Create and setup bot
    bot = DiscordBot()
    
    # Setup commands
    await setup_commands(bot)
    
    try:
        # Start the bot
        logger.info('Starting bot...')
        await bot.start(token)
    except discord.LoginFailure:
        logger.error('Invalid Discord token provided!')
    except discord.ConnectionClosed:
        logger.error('Connection to Discord was closed unexpectedly')
    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}')
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == '__main__':
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning('python-dotenv not available. Environment variables must be set manually.')
    
    import asyncio
    asyncio.run(main())
