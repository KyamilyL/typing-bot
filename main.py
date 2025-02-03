import discord
import config

from discord import app_commands

from command.practice import practice

client = config.client

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f"{client.user.name} is online!")
    await client.change_presence(activity=discord.Game(name=f"{len(client.guilds)} Servers!"))
    await tree.sync()

tree.add_command(practice)

client.run(config.TOKEN)