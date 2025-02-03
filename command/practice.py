import discord
import random
import time
import os

from discord import app_commands
from pyokaka import okaka
from config import client
from manager.user import running
from manager.word import load_words

words = load_words()

@app_commands.command(name="practice", description="タイピングの練習ができるよ！")
@app_commands.describe(difficulty="難易度をえらべるよ！")
@app_commands.choices(
    difficulty=[
        app_commands.Choice(name="easy", value="easy"),
        app_commands.Choice(name="normal", value="normal"),
        app_commands.Choice(name="hard", value="hard")
    ]
)
async def practice(interaction: discord.Interaction, difficulty: str = None):

    if interaction.user.id in running:
        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"実行中です。",
                color=0xff0064
            ),
            ephemeral=True
        )
        return
    
    running.add(interaction.user.id)

    if difficulty is None:
        difficulty = "easy"

    index = random.randint(0, len(words[difficulty]) - 1)
    word = words[difficulty][index]
    start = time.time()

    embed = discord.Embed(
        description=f"入力方法:`ローマ字` or `ひらがな`\n中止方法: `!stop`",
        color=0x00ff64,
    )
    embed.set_image(url=f"attachment://{index}.png")

    await interaction.response.send_message(
        embed=embed,
        file=discord.File(os.path.join(f"data/image/{difficulty}/{index}.png")),
        ephemeral=True
    )

    def check(message: discord.Message):
        if message.author.bot:
            return False
        return message.author.id == interaction.user.id and message.channel.id == interaction.channel.id
    
    while True:
        if time.time() - start > 30:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="時間切れ！"
                )
            )
            break

        message = await client.wait_for("message", check=check)

        print(f"{message.content} {okaka.convert(message.content)} {word[1]}")

        if okaka.convert(message.content.replace(" ", "")) == word[1]:
            await message.reply(
                embed=discord.Embed(
                    title="正解！",
                    description=f"{time.time() - start:.2f}秒"
                )
            )
            break
        else:
            try:
                if message.content == "!stop":
                    break

                await message.delete()
            except discord.NotFound:
                pass

    running.discard(interaction.user.id)