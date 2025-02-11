import discord
import config

from discord import app_commands

from command.ranking import ranking
from command.stop import stop
from command.typing import typing

from management.word import create_image

client = config.client

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f"{client.user.name} is online!")
    create_image()

    await client.change_presence(activity=discord.Game(name=f"{len(client.guilds)} Servers!"))
    await tree.sync()

tree.add_command(ranking)
tree.add_command(stop)
tree.add_command(typing)

client.run(config.TOKEN)