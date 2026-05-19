import discord
import wbse
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import random
from datetime import timedelta

# Load token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1473390630779490398  # your server ID
WELCOME_CHANNEL_ID = 1473390632210006149  # 🔁 PUT YOUR CHANNEL ID HERE

intents = discord.Intents.all()

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced!")

bot = MyBot(command_prefix="!", intents=intents)

warnings = {}
afk_users = {}

# ──────────────────────────────────────────────
# EVENTS
# ──────────────────────────────────────────────
@bot.event
async def on_disconnect():
    print("⚠️ Bot disconnected, reconnecting...")
    await asyncio.sleep(5)
    await bot.connect(reconnect=True)
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ✅ SIMPLE TAG WELCOME SYSTEM (ID BASED)

#with avatar in chat
@bot.event
async def on_member_join(member):
    try:
        channel = await bot.fetch_channel(WELCOME_CHANNEL_ID)

        embed = discord.Embed(
            title="🎉 Welcome!",
            description=f"WELCOME TO PARIPPUVADA, {member.mention}! 🎉 Hope you have an awesome time here!",
            color=discord.Color.green()
        )

        # ✅ show user's avatar
        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(content=member.mention, embed=embed)

    except Exception as e:
        print(f"❌ Welcome error: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f"✅ Welcome back {message.author.mention}")

    for user in message.mentions:
        if user.id in afk_users:
            await message.channel.send(f"💤 {user.name} is AFK: {afk_users[user.id]}")

    await bot.process_commands(message)

# ──────────────────────────────────────────────
# BASIC
# ──────────────────────────────────────────────

@bot.hybrid_command(description="Send a friendly greeting")
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention} 👋")

@bot.hybrid_command(description="Check the bot's latency")
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency * 1000)}ms")

@bot.hybrid_command(description="Roll a dice with a specified number of sides")
@app_commands.describe(sides="Number of sides on the dice")
async def roll(ctx, sides: int = 6):
    await ctx.send(f"🎲 {random.randint(1, sides)}")

@bot.hybrid_command(description="Flip a coin")
async def flip(ctx):
    await ctx.send(random.choice(["Heads 🪙", "Tails 🪙"]))

# ──────────────────────────────────────────────
# UTILITY
# ──────────────────────────────────────────────

@bot.hybrid_command(description="Get detailed information about a user")
@app_commands.describe(user="The user to inspect")
async def userinfo(ctx, user: discord.Member = None):
    user = user or ctx.author
    embed = discord.Embed(title=f"👤 {user}", color=discord.Color.blurple())
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Joined", value=user.joined_at.strftime("%b %d, %Y"))
    embed.set_thumbnail(url=user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.hybrid_command(description="Get server information")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📋 {guild.name}", color=discord.Color.green())
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"))
    await ctx.send(embed=embed)

@bot.hybrid_command(description="Get a user's avatar")
@app_commands.describe(user="User whose avatar you want")
async def avatar(ctx, user: discord.Member = None):
    user = user or ctx.author
    await ctx.send(user.display_avatar.url)

# ──────────────────────────────────────────────
# AFK
# ──────────────────────────────────────────────

@bot.hybrid_command(description="Set your AFK status")
@app_commands.describe(reason="Reason for AFK")
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = reason
    await ctx.send(f"💤 You are now AFK: {reason}")

# ──────────────────────────────────────────────
# WARN SYSTEM
# ──────────────────────────────────────────────

@bot.hybrid_command(description="Warn a user")
@app_commands.describe(user="User to warn", reason="Reason")
async def warn(ctx, user: discord.Member, *, reason="No reason"):
    warnings.setdefault(user.id, []).append(reason)
    await ctx.send(f"⚠️ {user} warned: {reason}")

@bot.hybrid_command(description="View warnings of a user")
@app_commands.describe(user="User to check")
async def warnings(ctx, user: discord.Member):
    user_warnings = warnings.get(user.id, [])
    if not user_warnings:
        return await ctx.send("✅ No warnings")
    await ctx.send("\n".join(user_warnings))

@bot.hybrid_command(description="Clear warnings of a user")
@app_commands.describe(user="User to clear")
async def clearwarnings(ctx, user: discord.Member):
    warnings.pop(user.id, None)
    await ctx.send("🧹 Warnings cleared")

# ──────────────────────────────────────────────
# MODERATION
# ──────────────────────────────────────────────

@bot.hybrid_command(description="Kick a user")
@app_commands.describe(user="User to kick", reason="Reason")
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason="No reason"):
    await user.kick(reason=reason)
    await ctx.send(f"👢 Kicked {user}")

@bot.hybrid_command(description="Ban a user")
@app_commands.describe(user="User to ban", reason="Reason")
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *, reason="No reason"):
    await user.ban(reason=reason)
    await ctx.send(f"🔨 Banned {user}")

@bot.hybrid_command(description="Mute a user")
@app_commands.describe(user="User to mute", minutes="Duration in minutes")
async def mute(ctx, user: discord.Member, minutes: int = 5):
    await user.timeout(discord.utils.utcnow() + timedelta(minutes=minutes))
    await ctx.send(f"🔇 Muted for {minutes} minutes")

@bot.hybrid_command(description="Unmute a user")
@app_commands.describe(user="User to unmute")
async def unmute(ctx, user: discord.Member):
    await user.timeout(None)
    await ctx.send("🔊 Unmuted")

# ──────────────────────────────────────────────
# FUN 
# ──────────────────────────────────────────────

@bot.hybrid_command(description="Guess a number between 1 and 10")
@app_commands.describe(number="Enter a number between 1 and 10")
async def guess(ctx, number: int):
    if number < 1 or number > 10:
        return await ctx.send("⚠️ Choose a number between 1 and 10")

    correct = random.randint(1, 10)
    if number == correct:
        await ctx.send("🎉 Correct! You guessed it!")
    else:
        await ctx.send(f"❌ Wrong! The number was **{correct}**")

@bot.hybrid_command(description="Play Rock Paper Scissors")
@app_commands.describe(choice="Choose rock, paper, or scissors")
@app_commands.choices(choice=[
    app_commands.Choice(name="Rock", value="rock"),
    app_commands.Choice(name="Paper", value="paper"),
    app_commands.Choice(name="Scissors", value="scissors")
])
async def rps(ctx, choice: app_commands.Choice[str]):
    bot_choice = random.choice(["rock", "paper", "scissors"])

    if choice.value == bot_choice:
        result = "It's a tie!"
    elif (
        (choice.value == "rock" and bot_choice == "scissors") or
        (choice.value == "paper" and bot_choice == "rock") or
        (choice.value == "scissors" and bot_choice == "paper")
    ):
        result = "You win! 🎉"
    else:
        result = "You lose! 😢"

    await ctx.send(f"You: **{choice.value}** | Bot: **{bot_choice}**\n{result}")

@bot.hybrid_command(description="Get a random joke")
async def joke(ctx):
    jokes = [
        "Why Python? Because it's sssssimple 🐍",
        "I told a UDP joke… you might not get it 😏",
        "Why do programmers hate nature? Too many bugs 🐛",
        "Why did the developer go broke? Because he used up all his cache 💸"
    ]
    await ctx.send(random.choice(jokes))

# ──────────────────────────────────────────────
# RUN
# ──────────────────────────────────────────────

wbse.keep_alive()
bot.run(TOKEN)
