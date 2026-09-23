import os
import time
import re
import httpx
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

BASE_URL = "https://discord.com/api/v10"

HEADERS = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json"
}

# Swear replacements
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

# Track last message ID to avoid duplicates
last_message_id = {}

def replace_swears(text):
    def repl(match):
        word = match.group(0).lower()
        return SWEAR_REPLACEMENTS.get(word, word)
    return pattern.sub(repl, text)

def get_messages(channel_id):
    url = f"{BASE_URL}/channels/{channel_id}/messages?limit=10"
    r = httpx.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return []

def delete_message(channel_id, message_id):
    url = f"{BASE_URL}/channels/{channel_id}/messages/{message_id}"
    httpx.delete(url, headers=HEADERS)

def get_or_create_webhook(channel_id):
    # Get existing webhooks
    url = f"{BASE_URL}/channels/{channel_id}/webhooks"
    r = httpx.get(url, headers=HEADERS)
    if r.status_code == 200:
        hooks = r.json()
        for h in hooks:
            if h["name"] == "SwearJar":
                return h["id"], h["token"]

    # Create new webhook
    url = f"{BASE_URL}/channels/{channel_id}/webhooks"
    r = httpx.post(url, headers=HEADERS, json={"name": "SwearJar"})
    data = r.json()
    return data["id"], data["token"]

def send_webhook(webhook_id, webhook_token, content, username, avatar_url):
    url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"
    httpx.post(url, json={
        "content": content,
        "username": username,
        "avatar_url": avatar_url
    })

def poll_channel(channel_id):
    global last_message_id

    messages = get_messages(channel_id)
    if not messages:
        return

    # Sort newest → oldest
    messages = sorted(messages, key=lambda m: int(m["id"]), reverse=True)

    for msg in messages:
        mid = msg["id"]

        # Skip already processed messages
        if last_message_id.get(channel_id) == mid:
            continue

        last_message_id[channel_id] = mid

        # Skip bot messages
        if msg.get("author", {}).get("bot"):
            continue

        content = msg.get("content", "")
        cleaned = replace_swears(content)

        if cleaned != content:
            # Delete original
            delete_message(channel_id, mid)

            # Send webhook replacement
            webhook_id, webhook_token = get_or_create_webhook(channel_id)
            send_webhook(
                webhook_id,
                webhook_token,
                cleaned,
                msg["author"]["username"],
                msg["author"]["avatar"]
            )

def main():
    print("Bot is running (REST mode)...")

    # Put your channel IDs here
    CHANNELS = [
        # Example:
        # 123456789012345678
    ]

    while True:
        for cid in CHANNELS:
            poll_channel(cid)

        time.sleep(2)  # Poll every 2 seconds

if __name__ == "__main__":
    main()
