import discord
import os
import time

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


Tablets = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}

@client.event
async def on_ready():
    print(f'{client.user} Ready !')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!Test'):
        await message.channel.send("Test")

client.run(os.getenv('TOKEN'))