import discord
from discord.ext import commands, tasks
from libs import contested_zone_timer
from libs import time_seed
from libs import lib

def get_timer_msg():
    timer_until_end = contested_zone_timer.get_time_until_end()
    light_status = contested_zone_timer.get_light_status()
    hangar_phase = contested_zone_timer.get_hangar_phase()
    time_until_next_phase = contested_zone_timer.get_time_until_next_phase()

    msg = "## --Executive Hangar Timer--\n"
    msg += f"                       **{lib.format_time(timer_until_end)}**\n"
    msg += f"           {light_status}\n\n"

    status_text = ""
    if hangar_phase == 'OPEN':
        status_text = f"Hangar Open   | Close in {lib.format_time(time_until_next_phase)}"
    elif hangar_phase == 'CLOSE':
        status_text = f"Hangar Closed | Opens in {lib.format_time(time_until_next_phase)}"
    else:
        status_text = "Hangar Reseting"
    msg += status_text
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

def parse_tablets(str_val: str):
    tablets = [0] * 7
    s = str_val.split()
    for tablet in s:
        tablets[int(tablet) - 1] += 1
    return tablets

class ContestedZoneCog(commands.Cog):
    def __init__(self, bot: commands.Bot, data: dict):
        self.bot = bot
        self.data = data
        self.update_hangar_message.start()

    def cog_unload(self):
        self.update_hangar_message.cancel()

    # Commands
    @commands.hybrid_command(name="cz_setup_timer", description="Affiche le panneau du timer de la zone contestée.")
    async def setup_timer(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)
        if self.data.get('timer_msg_id') and self.data.get('timer_channel_id'):
            message = await get_message(self.bot, self.data['timer_channel_id'], self.data['timer_msg_id'])
            if message:
                await message.delete()
        
        sent_message = await ctx.send(get_timer_msg())
        self.data['timer_msg_id'] = sent_message.id
        self.data['timer_channel_id'] = ctx.channel.id
        await lib.save_json(self.data, lib.DATA)

    @commands.hybrid_command(name="cz_add_tablets", description="Ajoute des tablettes à un joueur.")
    async def add_tablets(self, ctx: commands.Context, player: discord.Member, tablets_list: str):
        await ctx.defer(ephemeral=True)
        try:
            tablets = parse_tablets(tablets_list)
            player_id_str = str(player.id)
            if 'tablets' not in self.data or 'players' not in self.data['tablets']:
                self.data['tablets'] = {'players': {}}
            if player_id_str not in self.data['tablets']['players']:
                self.data['tablets']['players'][player_id_str] = [0] * 7
            for i in range(7):
                self.data['tablets']['players'][player_id_str][i] += tablets[i]
            await lib.save_json(self.data, lib.DATA)
            await ctx.send("Tablettes ajoutées !", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Erreur : {e}", ephemeral=True)

    @commands.hybrid_command(name="cz_remove_tablets", description="Retire des tablettes à un joueur.")
    async def remove_tablets(self, ctx: commands.Context, player: discord.Member, tablets_list: str):
        await ctx.defer(ephemeral=True)
        try:
            tablets = parse_tablets(tablets_list)
            player_id_str = str(player.id)
            
            if player_id_str not in self.data['tablets']['players']:
                await ctx.send(content="Erreur: joueur non trouvé.", ephemeral=True)
                return

            for i in range(7):
                self.data['tablets']['players'][player_id_str][i] -= tablets[i]
                if self.data['tablets']['players'][player_id_str][i] < 0:
                    # Annuler la transaction si le solde est négatif
                    for j in range(i + 1):
                        self.data['tablets']['players'][player_id_str][j] += tablets[j]
                    await ctx.send(content="Erreur: Pas assez de tablettes.", ephemeral=True)
                    return

            await lib.save_json(self.data, lib.DATA)
            await ctx.send(content="Tablettes retirées !", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Erreur : {e}", ephemeral=True)


    @commands.hybrid_command(name="cz_transfer_tablets", description="Transfère des tablettes entre joueurs.")
    async def transfer_tablets(self, ctx: commands.Context, from_player: discord.Member, to_player: discord.Member, tablets_list: str):
        await ctx.defer(ephemeral=True)
        try:
            tablets = parse_tablets(tablets_list)
            from_player_id_str = str(from_player.id)
            to_player_id_str = str(to_player.id)

            if from_player_id_str not in self.data['tablets']['players']:
                await ctx.send(content="Erreur: joueur source non trouvé.", ephemeral=True)
                return

            if to_player_id_str not in self.data['tablets']['players']:
                self.data['tablets']['players'][to_player_id_str] = [0] * 7

            # Vérification avant transfert
            for i in range(7):
                if self.data['tablets']['players'][from_player_id_str][i] < tablets[i]:
                    await ctx.send(content="Erreur: Le joueur source n'a pas assez de tablettes.", ephemeral=True)
                    return
            
            # Transfert
            for i in range(7):
                self.data['tablets']['players'][from_player_id_str][i] -= tablets[i]
                self.data['tablets']['players'][to_player_id_str][i] += tablets[i]

            await lib.save_json(self.data, lib.DATA)
            await ctx.send(content="Tablettes transférées !", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Erreur : {e}", ephemeral=True)

    @commands.hybrid_command(name="cz_tablets_status", description="Affiche l'état de toutes les tablettes collectées.")
    async def tablets_status(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)
        
        all_tablets = [0] * 7
        if 'tablets' in self.data and 'players' in self.data['tablets']:
            for player_tablets in self.data['tablets']['players'].values():
                for i in range(7):
                    all_tablets[i] += player_tablets[i]
        
        num_sets = min(all_tablets)
        total_tablets = sum(all_tablets)
        
        msg = "## 📊 **Rapport de Collecte des Tablettes**\n"

        header = "Tablette   | 1 | 2 | 3 | 4 | 5 | 6 | 7 |"
        separator = "-----------|---|---|---|---|---|---|---|"
        quantities_str = [f"{qty:^3}" for qty in all_tablets]
        body = f"Quantité   |{'|'.join(quantities_str)}|"

        msg += "```\n"
        msg += f"{header}\n"
        msg += f"{separator}\n"
        msg += f"{body}\n"
        msg += "```\n"

        msg += f"📦 **Total de tablettes collectées :** `{total_tablets}`\n"
        msg += f"💎 **Nombre de sets complets :** `{num_sets}`\n"

        await ctx.send(msg)

    @commands.hybrid_command(name="cz_update_time_seed", description="Met à jour le seed du timer (Admin).")
    @commands.has_permissions(administrator=True)
    async def update_time_seed(self, ctx: commands.Context):
        await ctx.defer(ephemeral=True)
        seed = await time_seed.update_time_seed()
        self.data['time_seed'] = seed
        contested_zone_timer.load_time_seed(self.data)
        await ctx.send(f"Time Seed mis à jour ! Nouveau seed : {seed}", ephemeral=True)

    # Task
    @tasks.loop(seconds=30)
    async def update_hangar_message(self):
        if 'timer_msg_id' not in self.data or self.data['timer_msg_id'] == 0:
            return
        message = await get_message(self.bot, self.data['timer_channel_id'], self.data['timer_msg_id'])
        if message:
            await message.edit(content=get_timer_msg())
        else:
            self.data['timer_msg_id'] = 0
            self.data['timer_channel_id'] = 0
            await lib.save_json(self.data, lib.DATA)

    @update_hangar_message.before_loop
    async def before_update_hangar_message(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    data = await lib.load_json(lib.DATA)
    await bot.add_cog(ContestedZoneCog(bot, data))