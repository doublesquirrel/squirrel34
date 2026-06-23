
import os
import random
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
R34_USER_ID = os.getenv("R34_USER_ID")
R34_API_KEY = os.getenv("R34_API_KEY")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ----------------------------------
# Rule34 Search
# ----------------------------------
async def search_rule34(tags: str):
    params = {
        "page": "dapi",
        "s": "post",
        "q": "index",
        "json": 1,
        "limit": 100,
        "tags": tags,
        "user_id": R34_USER_ID,
        "api_key": R34_API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.rule34.xxx/index.php",
            params=params
        ) as resp:

            if resp.status != 200:
                return []

            try:
                return await resp.json()
            except Exception:
                return []


# ----------------------------------
# Rule34 Tag Autocomplete
# ----------------------------------
async def rule34_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    if not current:
        return []

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://rule34.xxx/autocomplete.php?q={current}"
        ) as resp:

            if resp.status != 200:
                return []

            try:
                data = await resp.json()
            except Exception:
                return []

    choices = []

    for item in data[:25]:
        tag_name = item.get("value") or item.get("label")

        if tag_name:
            choices.append(
                app_commands.Choice(
                    name=tag_name[:100],
                    value=tag_name
                )
            )

    return choices


# ----------------------------------
# Slash Command
# ----------------------------------
@bot.tree.command(
    name="r34",
    description="Search Rule34"
)
@app_commands.describe(
    tag1="First tag",
    tag2="Second tag (optional)",
    tag3="Third tag (optional)"
)
@app_commands.autocomplete(
    tag1=rule34_autocomplete,
    tag2=rule34_autocomplete,
    tag3=rule34_autocomplete
)
async def r34(
    interaction: discord.Interaction,
    tag1: str,
    tag2: str | None = None,
    tag3: str | None = None,
):

    # NSFW only
    if not interaction.channel.is_nsfw():
        await interaction.response.send_message(
            "This command can only be used in NSFW channels.",
            ephemeral=True
        )
        return

    tags = [tag1]

    if tag2:
        tags.append(tag2)

    if tag3:
        tags.append(tag3)

    search_tags = " ".join(tags)

    await interaction.response.defer()

    results = await search_rule34(search_tags)

    if not results:
        await interaction.followup.send(
            f"No results found for `{search_tags}`"
        )
        return

    post = random.choice(results)

    file_url = post.get("file_url")

    if not file_url:
        await interaction.followup.send(
            "No media found."
        )
        return

    embed = discord.Embed(
        title="Rule34 Search",
        description=f"Tags: `{search_tags}`"
    )

    embed.set_image(url=file_url)

    await interaction.followup.send(
        embed=embed
    )


@bot.event
async def on_ready():
    synced = await bot.tree.sync()

    print(f"Logged in as {bot.user}")
    print(f"Synced {len(synced)} slash commands")


bot.run(TOKEN)

