import discord
import config

from discord import app_commands

from command.practice import practice
from command.ranking import ranking
from management.data.bestscore import setup_bestscore
from management.word import create_image

client = config.client

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f"{client.user.name} is online!")
    setup_bestscore()
    create_image()

    await client.change_presence(activity=discord.Game(name=f"{len(client.guilds)} Servers!"))
    await tree.sync()

tree.add_command(practice)
tree.add_command(ranking)

client.run(config.TOKEN)