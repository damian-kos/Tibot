import os
import discord

# Didn't understand cogs back then
from cogs import tibia_site_class
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
import json

# .env. By default, load_dotenv doesn't override existing environment variables.
load_dotenv()
# "DISCORD-TOKEN" z pliku .env
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

# message_content needs to be on on discord dev portal.
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# After connecting to guild returns channels and their names. Optionally can send "hello" message.
@client.event
async def on_ready():
    for guild in client.guilds:
        for channel in guild.channels:
            print(f"{channel} : {channel.id}")

    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})\n"
        f"{client.user} is connected to the following channel:\n"
        f"{channel.name}(id: {channel.id})"
    )


@client.event
async def on_message(message):
    if message.content.startswith("$Whois"):
        channel = client.get_channel(1011344365781786664)
        # Split Message into $Whois and a character name
        s = message.content.split(" ", 1)
        name = s[1]
        print(name)

        # --------------------- tibia_site.py ------------------------#

        character = tibia_site_class.Character(name)

        # Checks what vocation character is and returns an image which will be sent as a thumbnail.
        # TODO #1: Add images for non premium characters and non vocation.
        def vocation():
            voc = character.char_voc
            if "Knight" in voc:
                return "ek.gif"
            if "Paladin" in voc:
                return "rp.gif"
            if "Druid" in voc:
                return "ed.gif"
            if "Sorcerer" in voc:
                return "ms.gif"

        # ------------------ end of tibia_site.py --------------------#
        message_to_send = character.character_info_merge()
        url_name = s[1].replace(" ", "+")
        char_voc = vocation()
        if character.is_online():
            color = discord.Color.green()
        else:
            color = discord.Color.red()
        embed = discord.Embed(description=message_to_send, color=color)
        file = discord.File(f"chars/{char_voc}", filename="outfit.gif")
        embed.set_thumbnail(url="attachment://outfit.gif")
        embed.set_author(
            name="Tibia.com",
            url=f"https://www.tibia.com/community/?subtopic=characters&name={url_name}",
            icon_url="https://www.tibiawiki.com.br/images/7/76/Tibia_icon.png",
        )
        if character.format_highscores() != "":
            embed.add_field(
                name="Highscores",
                value=character.format_highscores(),
                inline=False,
            )

        await channel.send(embed=embed, file=file)


client.run(TOKEN)
