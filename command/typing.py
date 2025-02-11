import discord
import discord.ui
import random
import time
import asyncio

from discord import app_commands
from pyokaka import okaka
from config import client
from management.data.bestscore import get_bestscores, set_bestscore
from management.user import running
from management.word import load_words

words = load_words()

class modeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="一問だけ", style=discord.ButtonStyle.primary)
    async def once(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.updata_mode(interaction, button, "once")

    @discord.ui.button(label="スコアモード", style=discord.ButtonStyle.primary)
    async def score(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.updata_mode(interaction, button, "score")

    async def updata_mode(self, interaction: discord.Interaction, button: discord.ui.Button, mode):
        button.disabled = True
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="タイピング",
                description=f"モード: `{mode}`\n難易度: ` `"
            ),
            view=DifficultyView(mode)
        )

class DifficultyView(discord.ui.View):
    def __init__(self, mode):
        super().__init__(timeout=None)
        self.mode = mode

    @discord.ui.button(label="簡単", style=discord.ButtonStyle.success)
    async def easy(self, interaction: discord.Interaction, button: discord.ui.Button,):
        await self.update_difficulty(interaction, button, "easy")

    @discord.ui.button(label="普通", style=discord.ButtonStyle.primary)
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button,):
        await self.update_difficulty(interaction, button, "normal")

    @discord.ui.button(label="難しい", style=discord.ButtonStyle.danger)
    async def hard(self, interaction: discord.Interaction, button: discord.ui.Button,):
        await self.update_difficulty(interaction, button, "hard")

    async def update_difficulty(self, interaction: discord.Interaction, button:discord.ui.Button, difficulty):
        button.disabled = True
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="タイピング",
                description=f"モード: `{self.mode}`\n難易度: `{difficulty}`"
            ),
            view=None
        )

        await start_typing(interaction, self.mode, difficulty)

@app_commands.command(name="typing", description="タイピングの練習ができるよ！")
async def typing(interaction: discord.Interaction):

    if interaction.user.id in running:
        await interaction.response.send_message(
            embed=discord.Embed(
                description="実行中 `/stop`で中止可能",
                color=0xff6464
            ),
            ephemeral=True
        )
        return
    
    running.add(interaction.user.id)

    view = modeView()
    await interaction.response.send_message(
        embed=discord.Embed(
            title="タイピング",
            description=f"モード: ` `\n難易度: ` `",
            color=0x6464ff
        ),
        view=view,
        ephemeral=True
    )

async def start_typing(interaction: discord.Interaction, mode: str, difficulty: str):
    if mode == "once":
        index = random.randint(0, len(words[difficulty]) - 1)
        word = words[difficulty][index]

        embed = discord.Embed(
            description="📝入力方法: `ローマ字` `ひらがな` ⏳制限時間: `30秒`",
            color=0x6464ff,
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

        await interaction.followup.send(
            embed=discord.Embed(
                description="`!stop`で終了"
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
                        if message.content == "!stop":
                            break
                        
                        await message.add_reaction("❌")

                        streak = 0
                    except discord.NotFound:
                        pass
            except asyncio.TimeoutError:
                break
        
        scoreupdata = f"(自己ベスト: `{get_bestscores(difficulty, interaction.user.id)}点`)"
        if score >= get_bestscores(difficulty, interaction.user.id):
            set_bestscore(difficulty, interaction.user.id, score)
            scoreupdata = f"(ベスト更新！)"

        await interaction.followup.send(
            content=f"<@{interaction.user.id}>",
            embed=discord.Embed(
                title=f"結果 モード:{difficulty}",
                description=f"💯スコア: `{score}点` {scoreupdata}\n⚡入力速度: `{length / 60:.2f}文字/秒`\n🔥連続正解: `{max_streak}問`",
                color=0x6464ff
                )
            )

    running.discard(interaction.user.id)
