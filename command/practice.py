import discord
import random
import time
import asyncio

from discord import app_commands
from discord.ext import commands
from pyokaka import okaka
from config import client
from management.database import get_bestscore, set_bestscore
from management.user import running
from management.word import load_words

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
                description="実行中",
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
        embed.set_image(url=f"https://raw.githubusercontent.com/KyamilyL/typing-bot/refs/heads/main/asset/image/{difficulty}/{index}.png")

        await interaction.response.send_message(
            embed=embed,
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
            embed.set_image(url=f"https://raw.githubusercontent.com/KyamilyL/typing-bot/refs/heads/main/asset/image/{difficulty}/{index}.png")

            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )

            def check(message: discord.Message):
                if message.author.bot:
                    return False
                return message.author.id == interaction.user.id and message.channel.id == interaction.channel.id

            try:
                message = await client.wait_for("message", timeout=60 - (time.time() - start), check=check)
                if len(message.content.replace(" ", "")) < 100:
                    length += len(message.content.replace(" ", ""))

                if okaka.convert(message.content.replace(" ", "").lower()) == word[1]:
                    await message.add_reaction("⭕")

                    streak += 1
                    score += (100 * streak)
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

        set_bestscore(interaction.user.id, difficulty, score)
        await interaction.followup.send(
            content=f"<@{interaction.user.id}>",
            embed=discord.Embed(
                title=f"結果 モード:{difficulty}",
                description=f"💯スコア: `{score}点` (自己ベスト: `{get_bestscore(interaction.user.id, difficulty)}点`)\n⚡入力速度: `{length / 60:.2f}文字/秒`\n🔥連続正解: `{max_streak}問`",
                color=0x6464ff
                )
            )

    running.discard(interaction.user.id)
