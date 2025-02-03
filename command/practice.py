import discord
import random
import time
import asyncio
import pykakasi

from discord import app_commands
from discord.ui import View, Button
from pyokaka import okaka
from manager.word import load_words
from config import client

kakasi = pykakasi.kakasi()
kakasi.setMode("K", "H")
kakasi.setMode("J", "H")
conversion = kakasi.getConverter()

words = load_words()

running = set()

@app_commands.command(name="practice", description="タイピングの練習ができるよ！")
@app_commands.describe(mode="モードを選べるよ！")
@app_commands.describe(difficuly="難易度をえらべるよ！")
@app_commands.choices(
    mode=[
        app_commands.Choice(name="once", value=0),
        app_commands.Choice(name="score", value=1)
    ]
)
@app_commands.choices(
    difficuly=[
        app_commands.Choice(name="easy", value="easy"),
        app_commands.Choice(name="normal", value="normal"),
        app_commands.Choice(name="hard", value="hard")
    ]
)
async def practice(interaction: discord.Interaction, mode: int = None, difficuly: str = None):

    if interaction.user.id in running:
        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"実行中です"
            ),
            ephemeral=True
        )
        return
    else:
        running.add(interaction.user.id)

    if difficuly is None:
        difficuly = "easy"


    if mode is None or mode == 0:
        word = random.choice(words[difficuly])

        view = View()
        button = Button(label="中止", style=discord.ButtonStyle.red)

        async def button_callback(interaction: discord.Interaction):
            view.clear_items()
            running.discard(interaction.user.id)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description="canceled"
                ),
                view=view
            )
            return

        button.callback = button_callback
        view.add_item(button)

        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{word}"
            ),
            ephemeral=True,
            view=view
        )

        start_time = time.time()

        def check(message: discord.Message):
            if message.author.bot:
                return False

            return message.author.id == interaction.user.id and message.channel.id == interaction.channel.id

        try:
            while True:
                message = await client.wait_for("message", timeout=60.0, check=check)

                msg = message.content.replace(" ", "").replace("　", "")
                
                print(f"{msg} {conversion.do(word)}")

                end_time = time.time()
                elapsed_time = end_time - start_time

                if okaka.convert(msg) == conversion.do(word):
                    await message.reply(
                        embed=discord.Embed(
                            title="正解！",
                            description=f"{elapsed_time:.2f}秒"
                        )
                    )
                    break
                else:
                    try:
                        await message.delete()
                    except discord.NotFound:
                        pass

        except asyncio.TimeoutError:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="時間切れ！"
                )
            )
            
    else:
        running.discard(interaction.user.id)

    await interaction.delete_original_response()
    running.discard(interaction.user.id)