import discord
import random
import time
import asyncio
import os

from discord import app_commands
from discord.ext import commands
from pyokaka import okaka
from config import client
from manager.user import running
from manager.word import load_words

words = load_words()

@app_commands.command(name="practice", description="タイピングの練習ができるよ！")
@app_commands.describe(difficulty="難易度をえらべるよ！")
@app_commands.describe(mode="モードをえらべるよ！")
@app_commands.choices(
    difficulty=[
        app_commands.Choice(name="easy", value="easy"),
        app_commands.Choice(name="normal", value="normal"),
        app_commands.Choice(name="hard", value="hard")
    ]
)
@app_commands.choices(
    mode=[
        app_commands.Choice(name="once", value="once"),
        app_commands.Choice(name="score", value="score")
    ]
)
async def practice(interaction: discord.Interaction, difficulty: str = None, mode: str = None):

    if interaction.user.id in running:
        await interaction.response.send_message(
            embed=discord.Embed(
                description="⛔実行中",
                color=0xff6464
            ),
            ephemeral=True
        )
        return
    
    running.add(interaction.user.id)

    if difficulty is None:
        difficulty = "easy"

    if mode is None:
        mode = "once"

    if mode == "once":
        index = random.randint(0, len(words[difficulty]) - 1)
        word = words[difficulty][index]

        embed = discord.Embed(
            description="📝入力方法: `ローマ字` `ひらがな` ⏳制限時間: `30秒`",
            color=0x6464ff,
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

        try:
            start = time.time()
            message = await asyncio.wait_for(client.wait_for("message", check=check), timeout=30)

            if okaka.convert(message.content.replace(" ", "").lower()) == word[1]:
                await message.reply(
                    embed=discord.Embed(
                        title="⭕**正解！**",
                        description=f"⌛時間: `{time.time() - start:.2f}秒`⚡速度: `{len(message.content.replace(" ", "")) / (time.time() - start):.2f}文字/秒`",
                        colour=0x64ff64
                    )
                )

            else:
                try:
                    await message.reply(
                        embed=discord.Embed(
                            title="❌**不正解！**",
                            description=f"正解: `{word[1]}`\n入力: `{okaka.convert(message.content.replace(" ", "")).lower()}`",
                            colour=0xff6464
                    )
                )
                except discord.NotFound:
                    pass
        except asyncio.TimeoutError:
            await interaction.followup.send(
                embed=discord.Embed(
                    description="⌛時間切れ！",
                    colour=0xff6464
                ),
                ephemeral=True
            )
            await interaction.delete_original_response()
    else:
        start = time.time()
        score = 0
        length = 0
        streak = 0
        max_streak = 0

        await interaction.response.send_message(
            embed=discord.Embed(
                description="!stopで終了"
            ),
            ephemeral=True
        )

        while time.time() - start < 60:
            index = random.randint(0, len(words[difficulty]) - 1)
            word = words[difficulty][index]

            embed = discord.Embed(
                description=f"📝入力方法: `ローマ字` `ひらがな` ⏳残り時間: `{60 - (time.time() - start):.2f}秒`",
                color=0x6464ff
            )
            embed.set_image(url=f"attachment://{index}.png")

            await interaction.followup.send(
                embed=embed,
                file=discord.File(os.path.join(f"data/image/{difficulty}/{index}.png")),
                ephemeral=True
            )

            def check(message: discord.Message):
                if message.author.bot:
                    return False
                return message.author.id == interaction.user.id and message.channel.id == interaction.channel.id

            try:
                message = await client.wait_for("message", timeout=60 - (time.time() - start), check=check)
                if len(message.content.replace(" ", "")) < 30:
                    length += len(message.content.replace(" ", ""))

                if okaka.convert(message.content.replace(" ", "").lower()) == word[1]:
                    await message.add_reaction("⭕")

                    streak += 1
                    score += (10 * streak)
                    if streak > max_streak:
                        max_streak = streak
                else:
                    try:
                        if message.content.replace(" ", "") == "!stop":
                            break
                        
                        await message.add_reaction("❌")

                        streak = 0
                    except discord.NotFound:
                        pass
            except asyncio.TimeoutError:
                break

        await interaction.followup.send(
            embed=discord.Embed(
                title=f"結果 モード:{difficulty}",
                description=f"💯スコア: `{score + length}点` (自己ベスト: `1点`)\n⚡入力速度: `{length / 60:.2f}文字/秒`\n🔥連続正解: `{max_streak}問`",
                color=0x6464ff
                )
            )

    running.discard(interaction.user.id)