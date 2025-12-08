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
        lib.save_json(self.data, lib.DATA)

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
            lib.save_json(self.data, lib.DATA)
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

            lib.save_json(self.data, lib.DATA)
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

            lib.save_json(self.data, lib.DATA)
            await ctx.send(content="Tablettes transférées !", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Erreur : {e}", ephemeral=True)

    @commands.hybrid_command(name="cz_tablets_status", description="Affiche l'état de toutes les tablettes collectées.")
    async def tablets_status(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)
        
        if 'tablets' not in self.data or 'players' not in self.data['tablets']:
            await ctx.send("ℹ️ Aucune tablette n'a encore été enregistrée.")
            return
        
        # Filtrer les joueurs qui ont au moins une tablette
        players_with_tablets = {}
        for player_id, tablets in self.data['tablets']['players'].items():
            if sum(tablets) > 0:
                member = ctx.guild.get_member(int(player_id))
                player_name = member.display_name if member else f"Joueur {player_id}"
                players_with_tablets[player_name] = tablets
        
        if not players_with_tablets:
            await ctx.send("ℹ️ Aucune tablette n'a encore été collectée.")
            return
        
        # Calculer le total par tablette
        all_tablets = [0] * 7
        for tablets in players_with_tablets.values():
            for i in range(7):
                all_tablets[i] += tablets[i]
        
        num_sets = min(all_tablets)
        total_tablets = sum(all_tablets)
        
        msg = "## 📊 **Rapport de Collecte des Tablettes**\n"
        
        # Construire le tableau
        max_name_length = max(len(name) for name in players_with_tablets.keys())
        max_name_length = max(max_name_length, 18)  # Minimum pour "Joueur \ Tablettes"
        
        # En-tête
        header = f"{'Joueur \\ Tablettes':<{max_name_length}} | 1 | 2 | 3 | 4 | 5 | 6 | 7 "
        separator = "-" * len(header)
        
        msg += "```\n"
        msg += f"{header}\n"
        msg += f"{separator}\n"
        
        # Lignes des joueurs
        for player_name, tablets in sorted(players_with_tablets.items()):
            tablets_str = [f"{qty:^3}" for qty in tablets]
            line = f"{player_name:<{max_name_length}} |{'|'.join(tablets_str)}"
            msg += f"{line}\n"
        
        # Ligne de total
        msg += f"{separator}\n"
        totals_str = [f"{qty:^3}" for qty in all_tablets]
        total_line = f"{'TOTAL':<{max_name_length}} |{'|'.join(totals_str)}"
        msg += f"{total_line}\n"
        msg += "```\n"
        
        msg += f"💎 **Nombre de sets complets :** `{num_sets}`\n"
        
        await ctx.send(msg)

    @commands.hybrid_command(name="cz_hangars", description="Enregistre un hangar complété et retire un set complet de tablettes.")
    async def hangars(self, ctx: commands.Context, player: discord.Member):
        await ctx.defer(ephemeral=True)
        try:
            player_id_str = str(player.id)
            
            # Vérifier que le joueur existe
            if 'tablets' not in self.data or 'players' not in self.data['tablets']:
                await ctx.send("❌ Erreur: Aucune tablette enregistrée.", ephemeral=True)
                return
            
            if player_id_str not in self.data['tablets']['players']:
                await ctx.send(f"❌ Erreur: {player.display_name} n'a aucune tablette enregistrée.", ephemeral=True)
                return
            
            # Vérifier que le joueur a au moins 1 de chaque tablette (set complet)
            player_tablets = self.data['tablets']['players'][player_id_str]
            for i in range(7):
                if player_tablets[i] < 1:
                    await ctx.send(f"❌ Erreur: {player.display_name} n'a pas un set complet de tablettes.\nTablette #{i+1} manquante.", ephemeral=True)
                    return
            
            # Retirer 1 de chaque tablette
            for i in range(7):
                self.data['tablets']['players'][player_id_str][i] -= 1
            
            lib.save_json(self.data, lib.DATA)
            await ctx.send(f"✅ Hangar complété ! Un set de tablettes a été retiré à {player.display_name}.", ephemeral=True)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}", ephemeral=True)

    @commands.hybrid_command(name="cz_update_time_seed", description="Met à jour le seed du timer (Admin).")
    @commands.has_permissions(administrator=True)
    async def update_time_seed(self, ctx: commands.Context):
        await ctx.defer(ephemeral=True)
        seed = time_seed.update_time_seed()
        self.data['time_seed'] = seed
        contested_zone_timer.load_time_seed(self.data)
        await ctx.send(f"Time Seed mis à jour ! Nouveau seed : {seed}", ephemeral=True)

    # Task
    @tasks.loop(seconds=30)
    async def update_hangar_message(self):
        if self.data is None:
            self.data = lib.init_data()
        if 'timer_msg_id' not in self.data or self.data['timer_msg_id'] == 0:
            return
        message = await get_message(self.bot, self.data['timer_channel_id'], self.data['timer_msg_id'])
        if message:
            await message.edit(content=get_timer_msg())
        else:
            self.data['timer_msg_id'] = 0
            self.data['timer_channel_id'] = 0
            lib.save_json(self.data, lib.DATA)

    @update_hangar_message.before_loop
    async def before_update_hangar_message(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    data = lib.load_json(lib.DATA)
    await bot.add_cog(ContestedZoneCog(bot, data))