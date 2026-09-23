import os
import re
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Swear → funny replacement dictionary
SWEAR_REPLACEMENTS = {
    "fuck": "fudge nugget",
    "shit": "poop pancake",
    "bitch": "sass goblin",
    "ass": "booty bunker",
    "bastard": "rascal deluxe",
    "dick": "friendship stick",
    "piss": "lemon drizzle",
}

# Regex pattern for fast matching
pattern = re.compile(r"\b(" + "|".join(SWEAR_REPLACEMENTS.keys()) + r")\b", re.IGNORECASE)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

async def get_or_create_webhook(channel: discord.TextChannel):
    """Find an existing webhook or create one."""
    webhooks = await channel.webhooks()

    for hook in webhooks:
        if hook.name == "SwearJar":
            return hook

    return await channel.create_webhook(name="SwearJar")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    original = message.content

    # Replace swear words
    def replace(match):
        word = match.group(0).lower()
        return SWEAR_REPLACEMENTS.get(word, word)

    cleaned = pattern.sub(replace, original)

    # If nothing changed, do nothing
    if cleaned == original:
        await bot.process_commands(message)
        return

    # Delete original message
    try:
        await message.delete()
    except:
        pass

    # Get webhook
    webhook = await get_or_create_webhook(message.channel)

    # Rate-limit protection (max 4 msgs/sec)
    await asyncio.sleep(0.25)

    # Send via webhook with retry on 429
    try:
        await webhook.send(
            content=cleaned,
            username=message.author.display_name,
            avatar_url=message.author.display_avatar.url
        )
    except discord.HTTPException as e:
        if e.status == 429:
            await asyncio.sleep(e.retry_after)
            await webhook.send(
                content=cleaned,
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url
            )

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(TOKEN)
