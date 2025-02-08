@echo off

pip install discord.py
pip install audioop-lts
pip install python-dotenv
pip install asyncio
pip install pyokaka
pip install Pillow

if not exist .env echo TOKEN = "yourtokenhere" > .env

if not exist data mkdir data
if not exist data\bestscore.json echo {"easy": {},"normal": {}, "hard": {}} > data\bestscore.json

pause