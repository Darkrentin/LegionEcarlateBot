import discord
from discord.ext import commands
import os
import asyncio
from libs import contested_zone_timer
from libs import time_seed
from libs import lib
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

class LegionBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Load data once
        data = await lib.load_json(lib.DATA)
        if data is None:
            data = {} # Ensure data is a dict
        contested_zone_timer.load_time_seed(data)

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        synced = await self.tree.sync()
        print(f"all command synced ({len(synced)}.")

    async def on_ready(self):
        print(f'{self.user} is ready')

async def main():
    # Initialisation
    load_dotenv()
    time_seed.update_time_seed()
    data = lib.load_json(lib.DATA)
    contested_zone_timer.load_time_seed(data)

    bot = LegionBot()
    await bot.start(os.getenv('TOKEN'))

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")