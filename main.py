import os
import re
import asyncio
from dotenv import load_dotenv
import discord

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
client = discord.Client(intents=intents)

SWEAR_REPLACEMENTS = {
    "fuck": "fudge nugget",
    "shit": "poop pancake",
    "bitch": "sass goblin",
    "ass": "booty bunker",
    "bastard": "rascal deluxe",
    "dick": "friendship stick",
    "piss": "lemon drizzle",
}

pattern = re.compile(r"\b(" + "|".join(SWEAR_REPLACEMENTS.keys()) + r")\b", re.IGNORECASE)

async def get_or_create_webhook(channel):
    hooks = await channel.webhooks()
    for h in hooks:
        if h.name == "SwearJar":
            return h
    return await channel.create_webhook(name="SwearJar")

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    original = message.content

    def replace(match):
        word = match.group(0).lower()
        return SWEAR_REPLACEMENTS.get(word, word)

    cleaned = pattern.sub(replace, original)

    if cleaned == original:
        return

    try:
        await message.delete()
    except:
        pass

    webhook = await get_or_create_webhook(message.channel)

    await asyncio.sleep(0.25)

    await webhook.send(
        content=cleaned,
        username=message.author.display_name,
        avatar_url=message.author.display_avatar.url
    )

client.run(TOKEN)
