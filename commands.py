import discord
from discord.ext import commands
import time
import platform
import psutil
from config import BOT_CONFIG, COOLDOWN_CONFIG, VERIFICATION_CONFIG, GAME_ROLE_CONFIG, get_verification_settings, update_verification_settings, get_game_role_settings, update_game_role_settings, add_game_role, remove_game_role
import logging

logger = logging.getLogger('discord_bot.commands')

async def setup_commands(bot):
    """Setup all bot commands"""
    
    @bot.command(name='hello', help='Greet the bot')
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.user)
    async def hello(ctx):
        """Simple greeting command"""
        user = ctx.author
        embed = discord.Embed(
            title="👋 Hello!",
            description=f"Hello {user.mention}! How can I help you today?",
            color=BOT_CONFIG['embed_color']
        )
        embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.avatar.url if user.avatar else None)
        await ctx.send(embed=embed)
        logger.info(f'Hello command used by {user} in {ctx.guild}')
    
    @bot.command(name='ping', help='Check bot latency')
    @commands.cooldown(1, COOLDOWN_CONFIG['ping_cooldown'], commands.BucketType.user)
    async def ping(ctx):
        """Check bot's latency"""
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        end_time = time.time()
        
        # Calculate latencies
        api_latency = round(bot.latency * 1000, 2)
        message_latency = round((end_time - start_time) * 1000, 2)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=BOT_CONFIG['embed_color']
        )
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Message Latency", value=f"{message_latency}ms", inline=True)
        
        # Add status indicator based on latency
        if api_latency < 100:
            embed.add_field(name="Status", value="🟢 Excellent", inline=True)
        elif api_latency < 200:
            embed.add_field(name="Status", value="🟡 Good", inline=True)
        else:
            embed.add_field(name="Status", value="🔴 Poor", inline=True)
        
        await message.edit(content=None, embed=embed)
        logger.info(f'Ping command used by {ctx.author} - API: {api_latency}ms, Message: {message_latency}ms')
    
    @bot.command(name='info', aliases=['botinfo'], help='Get bot information')
    @commands.cooldown(1, COOLDOWN_CONFIG['info_cooldown'], commands.BucketType.guild)
    async def bot_info(ctx):
        """Display bot information"""
        embed = discord.Embed(
            title="🤖 Bot Information",
            description=BOT_CONFIG['description'],
            color=BOT_CONFIG['embed_color']
        )
        
        # Bot stats
        embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(set(bot.get_all_members())), inline=True)
        embed.add_field(name="Channels", value=len(set(bot.get_all_channels())), inline=True)
        
        # System info
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Prefix", value=BOT_CONFIG['prefix'], inline=True)
        
        # Performance info (if psutil is available)
        try:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            embed.add_field(name="CPU Usage", value=f"{cpu_usage}%", inline=True)
            embed.add_field(name="Memory Usage", value=f"{memory_usage}%", inline=True)
        except:
            pass
        
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
        
        embed.set_footer(text=f"Bot ID: {bot.user.id}")
        
        await ctx.send(embed=embed)
        logger.info(f'Info command used by {ctx.author} in {ctx.guild}')
    
    @bot.command(name='say', help='Make the bot say something')
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.user)
    async def say(ctx, *, message=None):
        """Make the bot repeat a message"""
        if not message:
            await ctx.send("❌ Please provide a message for me to say!")
            return
        
        # Delete the original command message for cleaner chat
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        
        # Send the message
        await ctx.send(message)
        logger.info(f'Say command used by {ctx.author}: {message}')
    
    @bot.command(name='serverinfo', aliases=['server'], help='Get server information')
    @commands.cooldown(1, COOLDOWN_CONFIG['info_cooldown'], commands.BucketType.guild)
    @commands.guild_only()
    async def server_info(ctx):
        """Display server information"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"🏰 {guild.name}",
            color=BOT_CONFIG['embed_color']
        )
        
        # Basic server info
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        
        # Member counts
        embed.add_field(name="Total Members", value=guild.member_count, inline=True)
        embed.add_field(name="Humans", value=len([m for m in guild.members if not m.bot]), inline=True)
        embed.add_field(name="Bots", value=len([m for m in guild.members if m.bot]), inline=True)
        
        # Channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        embed.add_field(name="Text Channels", value=text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await ctx.send(embed=embed)
        logger.info(f'Server info command used by {ctx.author} in {guild.name}')
    
    @bot.command(name='userinfo', aliases=['user'], help='Get user information')
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.user)
    async def user_info(ctx, user: discord.Member = None):
        """Display user information"""
        if user is None:
            user = ctx.author
        
        embed = discord.Embed(
            title=f"👤 {user.display_name}",
            color=BOT_CONFIG['embed_color']
        )
        
        embed.add_field(name="Username", value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        
        embed.add_field(name="Account Created", value=user.created_at.strftime("%B %d, %Y"), inline=True)
        
        if ctx.guild and user in ctx.guild.members and user.joined_at:
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%B %d, %Y"), inline=True)
            
            # Get top role (excluding @everyone)
            top_role = user.top_role if user.top_role.name != "@everyone" else None
            if top_role:
                embed.add_field(name="Top Role", value=top_role.mention, inline=True)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        
        await ctx.send(embed=embed)
        logger.info(f'User info command used by {ctx.author} for user {user}')
    
    @bot.command(name='embed', aliases=['createembed'], help='Create a custom embed')
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.user)
    async def create_embed(ctx, *, content=None):
        """Create a custom embed with various options"""
        if not content:
            # Show help message for embed creation
            help_embed = discord.Embed(
                title="🎨 Embed Creator Help",
                description="Create custom embeds with various options!",
                color=BOT_CONFIG['embed_color']
            )
            help_embed.add_field(
                name="📝 Usage",
                value=f"`{BOT_CONFIG['prefix']}embed title:Your Title | desc:Your Description | color:hex_color`",
                inline=False
            )
            help_embed.add_field(
                name="🎯 Available Options",
                value="""
**title:** Embed title
**desc:** Embed description  
**color:** Hex color (e.g., #ff0000 or ff0000)
**author:** Author name
**footer:** Footer text
**image:** Image URL
**thumbnail:** Thumbnail URL
**field:** Add field (format: name,value,inline)
                """,
                inline=False
            )
            help_embed.add_field(
                name="💡 Example",
                value=f"`{BOT_CONFIG['prefix']}embed title:Welcome! | desc:This is a custom embed | color:#00ff00 | author:Bot Creator | footer:Made with ❤️`",
                inline=False
            )
            await ctx.send(embed=help_embed)
            return
        
        # Parse the content for embed options
        embed_data = {}
        fields = []
        
        # Split by | to get different options
        options = content.split(' | ')
        
        for option in options:
            if ':' not in option:
                continue
                
            key, value = option.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == 'field':
                # Parse field: name,value,inline
                field_parts = value.split(',')
                if len(field_parts) >= 2:
                    field_name = field_parts[0].strip()
                    field_value = field_parts[1].strip()
                    field_inline = field_parts[2].strip().lower() == 'true' if len(field_parts) > 2 else False
                    fields.append({'name': field_name, 'value': field_value, 'inline': field_inline})
            else:
                embed_data[key] = value
        
        # Create the embed
        embed_title = embed_data.get('title', 'Custom Embed')
        embed_desc = embed_data.get('desc', embed_data.get('description', ''))
        
        # Handle color
        embed_color = BOT_CONFIG['embed_color']
        if 'color' in embed_data:
            color_value = embed_data['color']
            # Remove # if present
            if color_value.startswith('#'):
                color_value = color_value[1:]
            try:
                embed_color = int(color_value, 16)
            except ValueError:
                embed_color = BOT_CONFIG['embed_color']
        
        embed = discord.Embed(
            title=embed_title,
            description=embed_desc,
            color=embed_color
        )
        
        # Add author if specified
        if 'author' in embed_data:
            embed.set_author(name=embed_data['author'])
        
        # Add footer if specified
        if 'footer' in embed_data:
            embed.set_footer(text=embed_data['footer'])
        
        # Add image if specified
        if 'image' in embed_data:
            try:
                embed.set_image(url=embed_data['image'])
            except:
                pass
        
        # Add thumbnail if specified
        if 'thumbnail' in embed_data:
            try:
                embed.set_thumbnail(url=embed_data['thumbnail'])
            except:
                pass
        
        # Add fields
        for field in fields:
            embed.add_field(
                name=field['name'],
                value=field['value'],
                inline=field['inline']
            )
        
        # Send the embed
        try:
            await ctx.send(embed=embed)
            logger.info(f'Custom embed created by {ctx.author}')
            
            # Try to delete the original command message for cleaner chat
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
                
        except discord.HTTPException as e:
            await ctx.send(f"❌ Error creating embed: {str(e)}")
    
    @bot.command(name='embedtemplate', aliases=['embedtmpl'], help='Get embed templates')
    @commands.cooldown(1, COOLDOWN_CONFIG['info_cooldown'], commands.BucketType.user)
    async def embed_templates(ctx):
        """Show some embed templates for inspiration"""
        template_embed = discord.Embed(
            title="📋 Embed Templates",
            description="Copy and paste these templates, then customize them!",
            color=BOT_CONFIG['embed_color']
        )
        
        templates = [
            {
                "name": "🎉 Announcement",
                "value": f"`{BOT_CONFIG['prefix']}embed title:📢 Important Announcement | desc:We have exciting news to share! | color:#ffd700 | footer:Posted by Server Staff`"
            },
            {
                "name": "👋 Welcome Message", 
                "value": f"`{BOT_CONFIG['prefix']}embed title:Welcome to the Server! | desc:We're glad you're here! Make sure to read the rules. | color:#00ff00 | thumbnail:URL_HERE`"
            },
            {
                "name": "📊 Server Stats",
                "value": f"`{BOT_CONFIG['prefix']}embed title:📊 Server Statistics | color:#3498db | field:Members,500+ amazing people,true | field:Channels,25 different topics,true`"
            },
            {
                "name": "🎮 Game Event",
                "value": f"`{BOT_CONFIG['prefix']}embed title:🎮 Game Night Tonight! | desc:Join us for some fun games at 8 PM! | color:#9b59b6 | image:URL_HERE`"
            }
        ]
        
        for template in templates:
            template_embed.add_field(
                name=template["name"],
                value=template["value"],
                inline=False
            )
        
        await ctx.send(embed=template_embed)
        logger.info(f'Embed templates requested by {ctx.author}')
    
    @bot.command(name='setupverify', aliases=['verifysetup'], help='Setup verification system (Admin only)')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['info_cooldown'], commands.BucketType.guild)
    async def setup_verify(ctx, role: discord.Role, channel: discord.TextChannel = None):
        """Setup the verification system for the server"""
        if channel is None:
            channel = ctx.channel
        
        guild_id = ctx.guild.id
        settings = get_verification_settings(guild_id)
        
        # Create verification embed
        verify_embed = discord.Embed(
            title="🔐 Server Verification",
            description=settings['verify_message'],
            color=BOT_CONFIG['embed_color']
        )
        verify_embed.add_field(
            name="Instructions",
            value=f"React with {settings['emoji']} below to get the **{role.name}** role and access the server!",
            inline=False
        )
        verify_embed.set_footer(text="Verification System | One click to join!")
        
        # Send the verification message
        try:
            verify_message = await channel.send(embed=verify_embed)
            await verify_message.add_reaction(settings['emoji'])
            
            # Update settings
            update_verification_settings(
                guild_id,
                enabled=True,
                channel_id=channel.id,
                message_id=verify_message.id,
                role_id=role.id
            )
            
            # Confirmation message
            success_embed = discord.Embed(
                title="✅ Verification Setup Complete!",
                description=f"Verification system has been set up in {channel.mention}",
                color=0x00ff00
            )
            success_embed.add_field(name="Verification Role", value=role.mention, inline=True)
            success_embed.add_field(name="Verification Channel", value=channel.mention, inline=True)
            success_embed.add_field(name="Verification Emoji", value=settings['emoji'], inline=True)
            
            await ctx.send(embed=success_embed)
            logger.info(f'Verification system setup by {ctx.author} in {ctx.guild.name}')
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages or add reactions in that channel!")
        except Exception as e:
            await ctx.send(f"❌ Error setting up verification: {str(e)}")
    
    @bot.command(name='disableverify', help='Disable verification system (Admin only)')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def disable_verify(ctx):
        """Disable the verification system for the server"""
        guild_id = ctx.guild.id
        settings = get_verification_settings(guild_id)
        
        if not settings['enabled']:
            await ctx.send("❌ Verification system is not currently enabled!")
            return
        
        # Disable verification
        update_verification_settings(guild_id, enabled=False)
        
        embed = discord.Embed(
            title="🔓 Verification Disabled",
            description="Verification system has been disabled for this server.",
            color=0xff9900
        )
        await ctx.send(embed=embed)
        logger.info(f'Verification system disabled by {ctx.author} in {ctx.guild.name}')
    
    @bot.command(name='verifystatus', aliases=['vstatus'], help='Check verification system status')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def verify_status(ctx):
        """Check the current verification system status"""
        guild_id = ctx.guild.id
        settings = get_verification_settings(guild_id)
        
        embed = discord.Embed(
            title="🔍 Verification System Status",
            color=BOT_CONFIG['embed_color']
        )
        
        # Status
        status = "✅ Enabled" if settings['enabled'] else "❌ Disabled"
        embed.add_field(name="Status", value=status, inline=True)
        
        if settings['enabled']:
            # Get role, channel info
            role = ctx.guild.get_role(settings['role_id']) if settings['role_id'] else None
            channel = ctx.guild.get_channel(settings['channel_id']) if settings['channel_id'] else None
            
            embed.add_field(name="Verification Role", value=role.mention if role else "❌ Role not found", inline=True)
            embed.add_field(name="Verification Channel", value=channel.mention if channel else "❌ Channel not found", inline=True)
            embed.add_field(name="Reaction Emoji", value=settings['emoji'], inline=True)
            embed.add_field(name="Message ID", value=settings['message_id'] or "Not set", inline=True)
            
            # Check if verification message still exists
            if channel and settings['message_id']:
                try:
                    verify_message = await channel.fetch_message(settings['message_id'])
                    embed.add_field(name="Message Status", value="✅ Active", inline=True)
                except discord.NotFound:
                    embed.add_field(name="Message Status", value="❌ Message deleted", inline=True)
                except:
                    embed.add_field(name="Message Status", value="⚠️ Unable to check", inline=True)
        else:
            embed.add_field(name="Info", value="Use `!setupverify <role> [channel]` to enable verification", inline=False)
        
        await ctx.send(embed=embed)
    
    @bot.command(name='setwelcome', help='Set welcome message channel (Admin only)')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def set_welcome(ctx, channel: discord.TextChannel = None):
        """Set the welcome message channel"""
        if channel is None:
            channel = ctx.channel
        
        guild_id = ctx.guild.id
        update_verification_settings(guild_id, welcome_channel_id=channel.id)
        
        embed = discord.Embed(
            title="👋 Welcome Channel Set",
            description=f"Welcome messages will now be sent to {channel.mention}",
            color=BOT_CONFIG['embed_color']
        )
        await ctx.send(embed=embed)
        logger.info(f'Welcome channel set to {channel.name} by {ctx.author} in {ctx.guild.name}')
    
    # Handle setup_verify command errors
    @setup_verify.error
    async def setup_verify_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permissions to setup verification!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Please provide a valid role! Usage: `!setupverify @RoleName [#channel]`")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please specify a role! Usage: `!setupverify @RoleName [#channel]`")
    
    @bot.command(name='setupgameroles', aliases=['gamesetup'], help='Setup game role selection (Admin only)')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['info_cooldown'], commands.BucketType.guild)
    async def setup_game_roles(ctx, channel: discord.TextChannel = None):
        """Setup the game role selection system"""
        if channel is None:
            channel = ctx.channel
        
        guild_id = ctx.guild.id
        settings = get_game_role_settings(guild_id)
        
        # Check if there are any configured game roles
        if not settings['game_roles']:
            await ctx.send("❌ No game roles configured! Use `!addgamerole <emoji> @role` to add game roles first.")
            return
        
        # Create game role selection embed
        game_embed = discord.Embed(
            title=GAME_ROLE_CONFIG['embed_title'],
            description=GAME_ROLE_CONFIG['embed_description'],
            color=BOT_CONFIG['embed_color']
        )
        
        # Add game role options
        role_list = []
        emoji_list = []
        for emoji, role_id in settings['game_roles'].items():
            role = ctx.guild.get_role(role_id)
            if role:
                role_list.append(f"{emoji} - {role.name}")
                emoji_list.append(emoji)
        
        if role_list:
            game_embed.add_field(
                name="Available Game Roles",
                value="\n".join(role_list),
                inline=False
            )
            game_embed.add_field(
                name="Instructions",
                value=f"React with the emojis below to get/remove game roles!\nMaximum {settings['max_selections']} selections allowed.",
                inline=False
            )
            game_embed.set_footer(text="Game Role Selection | Click to join gaming communities!")
        
        # Send the game role message
        try:
            game_message = await channel.send(embed=game_embed)
            
            # Add reactions for all configured game roles
            for emoji in emoji_list:
                await game_message.add_reaction(emoji)
            
            # Update settings
            update_game_role_settings(
                guild_id,
                enabled=True,
                channel_id=channel.id,
                message_id=game_message.id
            )
            
            # Confirmation message
            success_embed = discord.Embed(
                title="✅ Game Role Selection Setup Complete!",
                description=f"Game role selection has been set up in {channel.mention}",
                color=0x00ff00
            )
            success_embed.add_field(name="Available Roles", value=f"{len(role_list)} game roles", inline=True)
            success_embed.add_field(name="Channel", value=channel.mention, inline=True)
            success_embed.add_field(name="Max Selections", value=settings['max_selections'], inline=True)
            
            await ctx.send(embed=success_embed)
            logger.info(f'Game role selection setup by {ctx.author} in {ctx.guild.name}')
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages or add reactions in that channel!")
        except Exception as e:
            await ctx.send(f"❌ Error setting up game roles: {str(e)}")
    
    @bot.command(name='addgamerole', help='Add a game role (Admin only)')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def add_game_role_cmd(ctx, emoji: str, role: discord.Role):
        """Add a game role mapping"""
        guild_id = ctx.guild.id
        
        # Add the game role mapping
        add_game_role(guild_id, emoji, role.id)
        
        embed = discord.Embed(
            title="✅ Game Role Added",
            description=f"Added game role: {emoji} → {role.mention}",
            color=BOT_CONFIG['embed_color']
        )
        embed.add_field(name="Next Step", value="Use `!setupgameroles` to create the selection message", inline=False)
        await ctx.send(embed=embed)
        logger.info(f'Game role {emoji} → {role.name} added by {ctx.author} in {ctx.guild.name}')
    
    @bot.command(name='removegamerole', help='Remove a game role (Admin only)')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def remove_game_role_cmd(ctx, emoji: str):
        """Remove a game role mapping"""
        guild_id = ctx.guild.id
        settings = get_game_role_settings(guild_id)
        
        if emoji not in settings['game_roles']:
            await ctx.send(f"❌ Game role with emoji {emoji} not found!")
            return
        
        # Get role info before removing
        role_id = settings['game_roles'][emoji]
        role = ctx.guild.get_role(role_id)
        role_name = role.name if role else "Unknown Role"
        
        # Remove the game role mapping
        remove_game_role(guild_id, emoji)
        
        embed = discord.Embed(
            title="🗑️ Game Role Removed",
            description=f"Removed game role: {emoji} → {role_name}",
            color=0xff9900
        )
        await ctx.send(embed=embed)
        logger.info(f'Game role {emoji} → {role_name} removed by {ctx.author} in {ctx.guild.name}')
    
    @bot.command(name='listgameroles', aliases=['gameroles'], help='List all configured game roles')
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def list_game_roles(ctx):
        """List all configured game roles"""
        guild_id = ctx.guild.id
        settings = get_game_role_settings(guild_id)
        
        embed = discord.Embed(
            title="🎮 Game Roles Configuration",
            color=BOT_CONFIG['embed_color']
        )
        
        # Status
        status = "✅ Enabled" if settings['enabled'] else "❌ Disabled"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Max Selections", value=settings['max_selections'], inline=True)
        
        # List configured roles
        if settings['game_roles']:
            role_list = []
            for emoji, role_id in settings['game_roles'].items():
                role = ctx.guild.get_role(role_id)
                if role:
                    role_list.append(f"{emoji} → {role.name}")
                else:
                    role_list.append(f"{emoji} → ❌ Role not found")
            
            embed.add_field(
                name=f"Configured Roles ({len(settings['game_roles'])})",
                value="\n".join(role_list) if role_list else "None",
                inline=False
            )
        else:
            embed.add_field(
                name="Configured Roles",
                value="No game roles configured\nUse `!addgamerole <emoji> @role` to add roles",
                inline=False
            )
        
        # Channel info
        if settings['enabled'] and settings['channel_id']:
            channel = ctx.guild.get_channel(settings['channel_id'])
            embed.add_field(name="Selection Channel", value=channel.mention if channel else "❌ Channel not found", inline=True)
            
            # Check message status
            if channel and settings['message_id']:
                try:
                    await channel.fetch_message(settings['message_id'])
                    embed.add_field(name="Message Status", value="✅ Active", inline=True)
                except discord.NotFound:
                    embed.add_field(name="Message Status", value="❌ Message deleted", inline=True)
                except:
                    embed.add_field(name="Message Status", value="⚠️ Unable to check", inline=True)
        
        await ctx.send(embed=embed)
    
    @bot.command(name='gamerolestatus', aliases=['grstatus'], help='Check game role system status')
    @commands.has_permissions(manage_guild=True) 
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def game_role_status(ctx):
        """Check the current game role system status"""
        await list_game_roles(ctx)  # Same as list_game_roles
    
    @bot.command(name='disablegameroles', help='Disable game role system (Admin only)')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.cooldown(1, COOLDOWN_CONFIG['default_cooldown'], commands.BucketType.guild)
    async def disable_game_roles(ctx):
        """Disable the game role system for the server"""
        guild_id = ctx.guild.id
        settings = get_game_role_settings(guild_id)
        
        if not settings['enabled']:
            await ctx.send("❌ Game role system is not currently enabled!")
            return
        
        # Disable game roles
        update_game_role_settings(guild_id, enabled=False)
        
        embed = discord.Embed(
            title="🎮 Game Roles Disabled",
            description="Game role selection system has been disabled for this server.",
            color=0xff9900
        )
        await ctx.send(embed=embed)
        logger.info(f'Game role system disabled by {ctx.author} in {ctx.guild.name}')
    
    logger.info('All commands have been loaded successfully')
