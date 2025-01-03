import discord
import asyncio
from discord.ext import commands
from discord.ui import Button, View
import random

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Star Citizens"))

@bot.event
async def on_member_remove(member):
    # Get the log channel
    log_channel = bot.get_channel(1323887893126709258)
    if log_channel:
        # Send a message to the log channel when a user leaves the server
        await log_channel.send(f"{member.name} has left the server.")

@bot.command()
async def hello(ctx):
    await ctx.send('I\'m Chris Roberts')

@bot.command()
async def spam(ctx, user_id: int = None, amount: int = None):
    if user_id is None or amount is None:
        await ctx.send("Please provide both user ID and amount. Usage: !spam <user_id> <amount>")
        return

    # Debug: Print user's roles
    print(f"User roles: {[role.id for role in ctx.author.roles]}")

    # Simply check if they have either of the allowed roles
    allowed_role_ids = [1170888683159818271, 1185726035585667162]
    has_permission = any(role.id in allowed_role_ids for role in ctx.author.roles)
    
    if not has_permission:
        await ctx.send("You have not server meshed yet!")
        return

    try:
        user = await bot.fetch_user(user_id)
        if user:
            messages_sent = 0
            amount = int(amount)  # Convert amount to integer
            
            while messages_sent < amount:
                try:
                    await user.send('im server meshing')
                    messages_sent += 1
                    if messages_sent % 5 == 0:  # Add delay every 5 messages
                        await asyncio.sleep(1)
                except discord.HTTPException as e:
                    if e.code == 429:  # Rate limit error
                        retry_after = e.retry_after
                        print(f"Rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        raise e

            await ctx.send(f"Successfully sent {messages_sent} messages to {user.name}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def ticket(ctx):
    # Get the specific channel where tickets should be created
    ticket_category = bot.get_channel(1282839031595667487)
    if not ticket_category:
        await ctx.send("Ticket category not found!")
        return

    # Create a more detailed embed
    embed = discord.Embed(
        title="🎫 Support Ticket System",
        description="Please select a category for your ticket below:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🚀 Server Meshing",
        value="Questions about server technology and performance",
        inline=False
    )
    embed.add_field(
        name="🤖 Star Citizens",
        value="General game support and community assistance",
        inline=False
    )
    embed.add_field(
        name="👨 Chris Roberts",
        value="Direct questions for Chris Roberts",
        inline=False
    )
    embed.set_footer(text="Click a button below to create your ticket")

    # Create a persistent view
    class TicketView(View):
        def __init__(self):
            super().__init__(timeout=None)  # Make the view persistent
            
        async def handle_ticket(self, interaction: discord.Interaction, ticket_type: str, emoji: str):
            # Check if user already has an open ticket
            existing_tickets = [
                channel for channel in ticket_category.channels
                if channel.name.startswith(f"ticket-{interaction.user.name.lower()}")
            ]
            
            if existing_tickets:
                await interaction.response.send_message(
                    f"You already have an open ticket! Please use {existing_tickets[0].mention}",
                    ephemeral=True
                )
                return

            # Create the ticket channel
            channel = await interaction.guild.create_text_channel(
                f"ticket-{interaction.user.name}-{ticket_type}",
                category=ticket_category,
                overwrites={
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
            )

            # Create welcome embed
            welcome_embed = discord.Embed(
                title=f"{emoji} New {ticket_type.replace('-', ' ').title()} Ticket",
                description=f"Welcome {interaction.user.mention}! Support will be with you shortly.",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            welcome_embed.add_field(
                name="Instructions",
                value="Please describe your issue in detail and wait for a response.\nTo close this ticket, use `!close`",
                inline=False
            )

            # Create close button
            close_button = Button(
                label="Close Ticket",
                emoji="🔒",
                style=discord.ButtonStyle.red,
                custom_id="close_ticket"
            )
            
            async def close_ticket_callback(close_interaction):
                if close_interaction.user == interaction.user or any(role.id in [1170888683159818271, 1185726035585667162] for role in close_interaction.user.roles):
                    await channel.delete()
                else:
                    await close_interaction.response.send_message("Only the ticket creator or staff can close this ticket!", ephemeral=True)

            close_button.callback = close_ticket_callback
            close_view = View()
            close_view.add_item(close_button)

            await channel.send(embed=welcome_embed, view=close_view)
            await interaction.response.send_message(f"Ticket created! Please check {channel.mention}", ephemeral=True)

        @discord.ui.button(label="Server Meshing", emoji="🚀", style=discord.ButtonStyle.green, custom_id="ticket_server_meshing")
        async def server_meshing(self, interaction: discord.Interaction, button: Button):
            await self.handle_ticket(interaction, "server-meshing", "🚀")
            
        @discord.ui.button(label="Star Citizens", emoji="🤖", style=discord.ButtonStyle.primary, custom_id="ticket_star_citizens")
        async def star_citizens(self, interaction: discord.Interaction, button: Button):
            await self.handle_ticket(interaction, "star-citizens", "🤖")
            
        @discord.ui.button(label="Chris Roberts", emoji="👨", style=discord.ButtonStyle.red, custom_id="ticket_chris_roberts")
        async def chris_roberts(self, interaction: discord.Interaction, button: Button):
            await self.handle_ticket(interaction, "chris-roberts", "👨")

    # Create and send the view
    view = TicketView()
    await ctx.send(embed=embed, view=view)

@bot.command()
async def ping(ctx, user_id: int = None, channel_id: int = None, amount: int = None):
    if user_id is None or channel_id is None or amount is None:
        await ctx.send("Please provide user ID, channel ID, and amount. Usage: !ping <user_id> <channel_id> <amount>")
        return

    # Debug: Print user's roles
    print(f"User roles: {[role.id for role in ctx.author.roles]}")

    # Simply check if they have either of the allowed roles
    allowed_role_ids = [1170888683159818271, 1185726035585667162]
    has_permission = any(role.id in allowed_role_ids for role in ctx.author.roles)
    
    if not has_permission:
        await ctx.send("You have not server meshed yet!")
        return

    try:
        user = await bot.fetch_user(user_id)
        channel = bot.get_channel(channel_id)
        
        if not channel:
            await ctx.send("Could not find channel with that ID.")
            return
            
        if not user:
            await ctx.send("Could not find user with that ID.")
            return

        messages_sent = 0
        amount = int(amount)  # Convert amount to integer
        
        while messages_sent < amount:
            try:
                await channel.send(f"<@{user_id}>")
                await channel.send("Im Chris Roberts and im going to server mesh")
                messages_sent += 1
                if messages_sent % 5 == 0:  # Add delay every 5 messages
                    await asyncio.sleep(1)
            except discord.HTTPException as e:
                if e.code == 429:  # Rate limit error
                    retry_after = e.retry_after
                    print(f"Rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    raise e

        await ctx.send(f"Finished pinging {user.name}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_message(message):
    # Check if the message mentions user 1066064609724874785
    if '<@1066064609724874785>' in message.content:
        await message.reply("Nope")
        await message.delete()
        await message.channel.send("Im Chris Roberts")
    
    # This line is necessary to make sure commands still work
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    role = member.guild.get_role(1181999662929023017)
    if role:
        await member.add_roles(role)

@bot.event
async def on_message_delete(message):
    # Skip if the message is from a bot to avoid potential loops
    if message.author.bot:
        return
        
    # Get the log channel
    log_channel = bot.get_channel(1323887893126709258)
    if log_channel:
        # Create an embed with the deleted message info
        embed = discord.Embed(
            title="Message Deleted",
            description=f"**Message:** {message.content}",
            color=discord.Color.red(),
            timestamp=message.created_at
        )
        embed.add_field(name="Author", value=f"{message.author.name} ({message.author.id})")
        embed.add_field(name="Channel", value=f"{message.channel.name} ({message.channel.id})")
        
        # Send the log
        await log_channel.send(embed=embed)

@bot.event
async def on_bulk_message_delete(messages):
    # Get the log channel
    log_channel = bot.get_channel(1323887893126709258)
    if log_channel:
        # Create a main embed for the bulk deletion
        main_embed = discord.Embed(
            title="Bulk Message Deletion",
            description=f"**{len(messages)} messages were deleted**",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=main_embed)

        # Log each deleted message
        for message in messages:
            if message.author.bot:
                continue
                
            embed = discord.Embed(
                description=f"**Message:** {message.content}",
                color=discord.Color.red(),
                timestamp=message.created_at
            )
            embed.add_field(name="Author", value=f"{message.author.name} ({message.author.id})")
            embed.add_field(name="Channel", value=f"{message.channel.name} ({message.channel.id})")
            
            await log_channel.send(embed=embed)

@bot.command()
async def steal(ctx):
    ships = [
        "Idris", "Javelin", "Bengal", "890 Jump", "Kraken",
        "Merchantman", "Carrack", "Reclaimer", "Hammerhead", "Perseus",
        "Polaris", "Odyssey", "Pioneer", "Nautilus", "Orion",
        "Endeavor", "Hull E", "Liberator", "Apollo", "Genesis Starliner",
        "Pegasus", "Retribution", "Kingship", "Merchantman", "A.R.K.",
        "Crucible", "Vulcan", "Corsair", "Mercury Star Runner", "Railen",
        "Spirit", "Raft", "Mule", "Expanse", "Legionnaire",
        "Scorpius", "Ares", "Redeemer", "Terrapin", "Valkyrie"
    ]
    
    outcomes = [
        "successfully stole",
        "failed to steal",
        "got caught trying to steal",
        "was arrested while attempting to steal",
        "server meshed away with",
        "tried to download",
        "attempted to right-click-save",
        "borrowed indefinitely",
        "accidentally purchased 10 copies of",
        "traded their house for",
        "sold their kidney to buy",
        "found a secret discount code for",
        "tried to trade a jpeg for",
        "got scammed trying to buy",
        "pledged their life savings for",
        "wrote a strongly worded letter about",
        "filed a complaint to the BBB about",
        "created a 30-minute YouTube video about",
        "started a Reddit thread about",
        "made a PowerPoint presentation explaining why they deserve"
    ]

    # 1% chance for the special outcome
    if random.random() < 0.01:
        await ctx.send(f"🌟 **LEGENDARY HEIST** 🌟\n{ctx.author.mention} has achieved the impossible and stolen Chris Roberts' personal computer with Star Citizen 4.0 and Server Meshing! The prophecy is fulfilled! 🚀✨")
        return
    
    ship = random.choice(ships)
    outcome = random.choice(outcomes)
    
    await ctx.send(f"🚀 {ctx.author.mention} {outcome} Chris Roberts' {ship}! 🚀")

@bot.event
async def on_voice_state_update(member, before, after):
    voice_channel_ids = [
        1168000992181239972,  # Original channel
        1214711733357248582,
        1180184659318018239,
        1204244397001019442,
        1204244281192091738,
        1208954017359724596,
        1170153783674814484,
        1302814607890710568
    ]
    notification_channel_id = 1307384949577482341
    notification_channel = bot.get_channel(notification_channel_id)
    
    # Check if user joined any of the specific voice channels
    if after.channel and after.channel.id in voice_channel_ids and before.channel != after.channel:
        await notification_channel.send(f"Chris Roberts has detected {member.mention} (ID: {member.id}) has joined the vc")
    
    # Check if user left any of the specific voice channels
    elif before.channel and before.channel.id in voice_channel_ids and before.channel != after.channel:
        await notification_channel.send(f"Chris Roberts has detected {member.mention} (ID: {member.id}) has left the vc")

@bot.command()
async def ijustbrownedeverywhere(ctx):
    await ctx.send("i love quantum travingling and i love trying inovatinve ways to fighure out how to server mesh and my name iws chris robers and my favorate person is salty mike and my new up in coming project is sqauron 42")

@bot.command()
async def kick(ctx, user_id: int = None):
    if not user_id:
        await ctx.send("Please provide a user ID. Usage: !kick <user_id>")
        return

    # Get user's roles
    user_roles = [role.id for role in ctx.author.roles]
    
    # Check if user has the restricted role but not the allowed roles
    has_restricted_role = 1181999662929023017 in user_roles
    has_allowed_role = any(role_id in user_roles for role_id in [1170888683159818271, 1185726035585667162])
    
    # If they only have the restricted role (and not any allowed roles), deny access
    if has_restricted_role and not has_allowed_role:
        await ctx.send("You have not server meshed yet!")
        return

    # Get the member object
    member = ctx.guild.get_member(user_id)
    
    if not member:
        await ctx.send("Could not find user with that ID.")
        return
        
    if not member.voice:
        await ctx.send("That user is not in a voice channel.")
        return

    try:
        await member.move_to(None)  # This disconnects them from voice
        await ctx.send(f"Successfully kicked {member.mention} from voice channel!")
    except Exception as e:
        await ctx.send(f"Failed to kick user: {str(e)}")

@bot.command()
async def close(ctx):
    # Check if the command is used in a ticket channel
    if not ctx.channel.name.startswith('ticket-'):
        await ctx.send("This command can only be used in ticket channels!")
        return

    # Check if the user has permission to close the ticket
    # Allow ticket creator (check if their name is in the channel name) or staff roles
    is_ticket_creator = ctx.author.name.lower() in ctx.channel.name.lower()
    is_staff = any(role.id in [1170888683159818271, 1185726035585667162] for role in ctx.author.roles)

    if not (is_ticket_creator or is_staff):
        await ctx.send("You don't have permission to close this ticket!")
        return

    # Create confirmation embed
    embed = discord.Embed(
        title="Ticket Closing",
        description="Are you sure you want to close this ticket?",
        color=discord.Color.yellow()
    )

    # Create confirmation buttons
    confirm_button = Button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        custom_id="confirm_close"
    )
    cancel_button = Button(
        label="Cancel",
        style=discord.ButtonStyle.red,
        custom_id="cancel_close"
    )

    async def confirm_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message("Only the person who initiated the close can confirm it!", ephemeral=True)
            return
        
        await interaction.message.edit(
            embed=discord.Embed(
                title="Ticket Closing",
                description="Ticket will be closed in 5 seconds...",
                color=discord.Color.red()
            ),
            view=None
        )
        await asyncio.sleep(5)
        await ctx.channel.delete()

    async def cancel_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message("Only the person who initiated the close can cancel it!", ephemeral=True)
            return
            
        await interaction.message.edit(
            embed=discord.Embed(
                title="Ticket Closing",
                description="Ticket closure cancelled.",
                color=discord.Color.green()
            ),
            view=None
        )

    confirm_button.callback = confirm_callback
    cancel_button.callback = cancel_callback

    view = View(timeout=60)  # 60 second timeout
    view.add_item(confirm_button)
    view.add_item(cancel_button)

    await ctx.send(embed=embed, view=view)

@bot.command(name='r')
async def relay_message(ctx, *, message: str = None):
    # Check if a message was provided
    if not message:
        await ctx.send("Please provide a message to relay!")
        return

    try:
        # Get the target channel
        target_channel = bot.get_channel(1324523377486069790)
        
        if not target_channel:
            await ctx.send("Could not find the target channel!")
            print(f"Debug: Could not find channel {1324523377486069790}")  # Debug line
            return

        # Send the message to the target channel
        await target_channel.send(message)
        
        # Send confirmation to the user
        await ctx.message.add_reaction('✅')
        
    except discord.Forbidden:
        await ctx.send("The bot doesn't have permission to send messages in the target channel.")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to send message: {str(e)}")
    except Exception as e:
        print(f"Error in relay_message: {type(e).__name__}: {str(e)}")  # Debug line
        await ctx.send(f"An error occurred: {str(e)}")

bot.run('MTMyMzg3NjAyNDIyNzk5MTY1Mw.GhDcPW.5YxSILPqGscGhdngOZfH03Z4kGjFVKUZSQgnfc')
