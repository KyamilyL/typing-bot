import discord

from discord import app_commands
from management.user import running

@app_commands.command(name="stop", description="中止")
async def stop(interaction: discord.Interaction):
    running.discard(interaction.user.id)
    await interaction.response.send_message(content="中止しました", ephemeral=True)