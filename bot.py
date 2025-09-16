import discord
from discord.ext import commands
import os
import time
import contested_zone_timer
import time_seed
import lib

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

data = {}
Tablets = {1:0,2:0,3:0,4:0,5:0,6:0,7:0}

@bot.event
async def on_ready():
    print(f'{bot.user} Ready !')
    synced = await bot.tree.sync()  
    print(f"All Command Sync {len(synced)}")

def get_timer_msg():
    timer_until_end = contested_zone_timer.get_time_until_end()
    light_status = contested_zone_timer.get_light_status()
    hangar_phase = contested_zone_timer.get_hangar_phase()
    time_until_next_phase = contested_zone_timer.get_time_until_next_phase()

    msg = ""
    msg+= "## --Executive Hangar Timer--\n"
    msg+=f"                       **{lib.format_time(timer_until_end)}**\n"
    msg+=f"           {light_status}\n\n"

    status_text =""
    if hangar_phase == 'OPEN':
        status_text = f"Hangar Open   | Close in {lib.format_time(time_until_next_phase)}"
    elif hangar_phase == 'CLOSE':
        status_text = f"Hangar Closed | Opens in {lib.format_time(time_until_next_phase)}"
    else:
        status_text = f"Hangar Reseting"

    msg+=status_text

    return msg

async def get_message(bot, channel_id, message_id):
    try:
        channel = bot.get_channel(channel_id)
        if not channel:
            return None
        message = await channel.fetch_message(message_id)
        return message
    except:
        return None

@bot.tree.command(name="setup_timer")
async def setup_timer(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)

    if data['timer_msg_id']!=0 and data['timer_channel_id']!=0:
        message = await get_message(bot, data['timer_channel_id'], data['timer_msg_id'])
        if message: # Check if message was found
            await message.delete()

    sent_message = await interaction.followup.send(get_timer_msg(),ephemeral=False)
    
    data['timer_msg_id'] = sent_message.id
    data['timer_channel_id'] = interaction.channel.id

    lib.save_json(data)

@bot.tree.command(name="update_timer")
async def update_timer(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if data['timer_msg_id'] == 0 or data['timer_channel_id'] == 0:
        await interaction.followup.send("timer error", ephemeral=True)
    else:
        message = await get_message(bot, data['timer_channel_id'], data['timer_msg_id'])
        if message:
            await message.edit(content=get_timer_msg())
            await interaction.followup.send(content="Update!", ephemeral=True)


def parse_tablets(str: str):
    tablets= [0]*7
    s = str.split()
    for tablet in s:
        tablets[int(tablet)-1]+=1
    return tablets




@bot.tree.command(name="add_tablets")
async def add_tablets(interaction: discord.Interaction, player: discord.Member, tablets_list: str):
    await interaction.response.defer(ephemeral=True)

    try:
        tablets = parse_tablets(tablets_list)
        player_id_str = str(player.id)

        if 'tablets' not in data or 'players' not in data['tablets']:
            data['tablets'] = {'players': {}}
        
        if player_id_str not in data['tablets']['players']:
            data['tablets']['players'][player_id_str] = [0] * 7

        for i in range(7):
            data['tablets']['players'][player_id_str][i] += tablets[i]
        
        lib.save_json(data)
        await interaction.followup.send(content="Tablets added !", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"error : {e}", ephemeral=True)

@bot.tree.command(name="remove_tablets")
async def remove_tablets(interaction: discord.Interaction, player: discord.Member, tablets_list: str):
    await interaction.response.defer(ephemeral=True)

    try:
        tablets = parse_tablets(tablets_list)
        player_id_str = str(player.id)
        
        if player_id_str not in data['tablets']['players']:
            await interaction.followup.send(content="Erreur: joueur non trouvé.", ephemeral=True)
            return

        for i in range(7):
            data['tablets']['players'][player_id_str][i] -= tablets[i]
            if data['tablets']['players'][player_id_str][i] < 0:
                await interaction.followup.send(content="error: Not enough tablets", ephemeral=True)
                return

        lib.save_json(data)
        await interaction.followup.send(content="tablets removed !", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"error: {e}", ephemeral=True)

@bot.tree.command(name="transfer_tablets")
async def transfer_tablets(interaction: discord.Interaction, from_player: discord.Member, to_player: discord.Member, tablets_list: str):
    await interaction.response.defer(ephemeral=True)

    try:
        tablets = parse_tablets(tablets_list)
        from_player_id_str = str(from_player.id)
        to_player_id_str = str(to_player.id)

        if from_player_id_str not in data['tablets']['players']:
            await interaction.followup.send(content="Erreur: joueur source non trouvé.", ephemeral=True)
            return

        if to_player_id_str not in data['tablets']['players']:
            data['tablets']['players'][to_player_id_str] = [0] * 7

        for i in range(7):
            data['tablets']['players'][from_player_id_str][i] -= tablets[i]
            data['tablets']['players'][to_player_id_str][i] += tablets[i]
            if data['tablets']['players'][from_player_id_str][i] < 0:
                await interaction.followup.send(content="error: Not enough tablets", ephemeral=True)
                return

        lib.save_json(data)
        await interaction.followup.send(content="tablets transferred !", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"error: {e}", ephemeral=True)

def get_all_tablets():
    global data
    
    tablets = [0] * 7
    if 'tablets' in data and 'players' in data['tablets']:
        for player_id, player_tablets in data['tablets']['players'].items():
            for i in range(7):
                tablets[i] += player_tablets[i]
    return tablets

def get_number_of_valid_set(tablets):
    return tablets.index(min(tablets))


@bot.tree.command(name="tablets_status")
async def tablets_status(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    
    msg = "## -----------Tablets Status----------\n"
    msg += "Tablets      | :one: | :two: | :three: | :four: | :five: | :six: | :seven: |\n"
    
    tablets = get_all_tablets()
    
    msg += "Quantity   | " + "  | ".join(f"{v:02d}" for v in tablets) + " |\n"
    
    await interaction.followup.send(msg,ephemeral=False)

@bot.tree.command(name="update_time_seed")
async def update_time_seed(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    seed = time_seed.update_time_seed()

    await interaction.followup.send(f"Time Seed Updated ! New seed : {seed}",ephemeral=True)



def main():
    global data

    time_seed.update_time_seed()
    contested_zone_timer.load_time_seed()
    data = lib.load_json()

    bot.run(os.getenv('TOKEN'))

if __name__ == '__main__':
    main()