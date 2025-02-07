import discord
import datetime

from discord import app_commands
from management.data.bestscore import load_bestscores
from management.user import running
from config import client

@app_commands.command(name="ranking", description="ランキングを見れるよ！")
@app_commands.describe(difficulty="難易度をえらべるよ！")
@app_commands.describe(type="ランキングの種類をえらべるよ！")
@app_commands.choices(
    difficulty=[
        app_commands.Choice(name="easy", value="easy"),
        app_commands.Choice(name="normal", value="normal"),
        app_commands.Choice(name="hard", value="hard")
    ]
)
@app_commands.choices(
    type=[
        app_commands.Choice(name="server", value="server"),
        app_commands.Choice(name="global", value="global")
    ]
)
async def ranking(interaction: discord.Interaction, difficulty: str = None, type: str = None):

    if interaction.user.id in running:
        await interaction.response.send_message(
            embed=discord.Embed(
                description="実行中",
                color=0xff6464
            ),
            ephemeral=True
        )
        return
    
    data = load_bestscores()
    
    if difficulty is None:
        difficulty = "easy"

    if type is None:
        type = "server"

    if type == "server":
        guild = client.get_guild(interaction.guild.id)
        members = {str(member.id) for member in guild.members}
        users = sorted(
            [userid for userid in data[difficulty] if userid in members],
            key=lambda user: data[difficulty][user],
            reverse=True
        )
        
        await interaction.response.send_message(embed=discord.Embed(
            title=f"ランキング モード:{difficulty}",
            description="\n".join([f"**#{i+1}** <@{user}>: `{data[difficulty][user]}点`" for i, user in enumerate(users[:10])]),
            colour=0x6464ff
        ))
    else:
        users = sorted(
            [userid for userid in data[difficulty]],
            key=lambda user: data[difficulty][user],
            reverse=True
        )

        await interaction.response.send_message(embed=discord.Embed(
            title=f"グローバルランキング モード:{difficulty}",
            description="\n".join([f"**#{i+1}** <@{user}>: `{data[difficulty][user]}点`" for i, user in enumerate(users[:10])]),
            colour=0x6464ff
        ))
