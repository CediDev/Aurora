
import asyncio
from discord import Intents
from discord.ext.commands import Bot
import logging
import discord
logging.basicConfig(level="INFO")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

with open("TOKEN.txt") as f:
  token = f.read().strip()

async def main():
  bot = Bot(command_prefix="!", intents=intents, activity=discord.Game(name="!Help")) 
  await bot.load_extension("commands")
  await bot.load_extension("events")
  await bot.start(token)
  
  

if __name__ == "__main__":
  asyncio.run(main())


