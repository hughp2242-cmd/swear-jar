import os
import re
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

    # Create new webhook
    return await channel.create_webhook(name="SwearJar")

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return

    original = message.content

    # Replace swear words with funny alternatives
    def replace(match):
        word = match.group(0).lower()
        return SWEAR_REPLACEMENTS.get(word, word)

    cleaned = pattern.sub(replace, original)

    # If nothing changed, do nothing
    if cleaned == original:
        await bot.process_commands(message)
        return

    # Delete the original message
    try:
        await message.delete()
    except:
        pass  # Bot may not have permission

    # Send cleaned message via webhook
    webhook = await get_or_create_webhook(message.channel)

    await webhook.send(
        content=cleaned,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url
    )

    await bot.process_commands(message)

# Simple command to test bot is alive
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(TOKEN)
