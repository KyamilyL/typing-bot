import discord
import dotenv
import os

intents = discord.Intents.default()

intents.members = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")