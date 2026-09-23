import os
import re
import asyncio
import hikari
import lightbulb
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = lightbulb.BotApp(
    token=TOKEN,
    intents=hikari.Intents.ALL,
)

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
    hooks = await channel.fetch_webhooks()
    for h in hooks:
        if h.name == "SwearJar":
            return h
    return await channel.create_webhook(name="SwearJar")

@bot.listen(hikari.GuildMessageCreateEvent)
async def on_message(event):
    message = event.message

    if not message.content or message.author.is_bot:
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

    webhook = await get_or_create_webhook(message.channel_id)

    await asyncio.sleep(0.25)

    await webhook.execute(
        content=cleaned,
        username=message.author.username,
        avatar_url=message.author.avatar_url,
    )

bot.run()
