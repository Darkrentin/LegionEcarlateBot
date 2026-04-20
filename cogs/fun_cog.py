import discord
from discord.ext import commands, tasks
from libs import lib
import random

SQ42_RELEASE_DATE = "2026-05-14 16:00:00"


def format_custom_float(n):
    if n == int(n):
        return str(int(n))
    
    s = f"{n:.15f}"
    decimal_part = s.split(".")[1]

    first_nonzero_pos = 0
    for i, digit in enumerate(decimal_part):
        if digit != '0':
            first_nonzero_pos = i + 1
            break
            
    result = f"{n:.{first_nonzero_pos}f}"
    
    return result.rstrip('0').rstrip('.')

def get_sample(data):
    diff = round(lib.get_dif_seconds(SQ42_RELEASE_DATE))
    if(diff == "error"):
        return []
    
    sample = random.sample(data, 5)

    res = []
    for time in sample:
        sec = time["sec"]
        text = time["text"]

        fact = diff / sec

        fact = format_custom_float(fact)

        res.append(f"- {str(fact)} **{text}**")

    return res
    



class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot, data: dict):
        self.bot = bot
        self.data = data

    @commands.hybrid_command(name="sq42soon", description="Affiche le temps restant avant l'Invictus") #"Affiche le temps restant avant la sortie de Squadron 42."
    async def get_timer(self, ctx: commands.Context):
        msg = "## On a \"**peut-être**\" des infos sur Squadron 42 (Invictus Launch Week) dans :\n"#"## **Squadron 42** sort dans :\n"

        sample = get_sample(self.data)

        for t in sample:
            msg += t + "\n"

        await ctx.send(msg)

async def setup(bot: commands.Bot):
    data = lib.load_json(lib.TIME)
    await bot.add_cog(FunCog(bot, data))