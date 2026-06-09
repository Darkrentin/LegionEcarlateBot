import discord
from discord import app_commands
from discord.ext import commands, tasks
from libs import lib
from libs import fleet_manager

class FleetManagerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, data: dict, ship_list: list):
        self.bot = bot
        self.data = data
        self.shipList = ship_list
    
    async def ship_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=ship, value=ship)
            for ship in self.shipList if current.lower() in ship.lower()
        ][:25] 

    @commands.hybrid_command(name="fl_add_in_game_ship", description="Ajoute un vaisseau à votre flotte disponible en jeu.")
    @app_commands.autocomplete(ship=ship_autocomplete)
    async def add_in_game_ship(self, ctx: commands.Context, ship: str):
        await ctx.defer(ephemeral=True)
        try:
            player_id_str = str(ctx.author.id)
            if player_id_str not in self.data:
                self.data[player_id_str] = { "InGame": [], "OnRSI": []}
            self.data[player_id_str]["InGame"].append(ship)
            lib.save_json(self.data,lib.FLEET)
            await ctx.send(f"✅ **{ship}** a été ajouté à votre flotte **en jeu**.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ **Erreur :** {e}", ephemeral=True)

    @commands.hybrid_command(name="fl_add_on_rsi_ship", description="Ajoute un vaisseau à votre flotte listée sur le site RSI (hangar).")
    @app_commands.autocomplete(ship=ship_autocomplete)
    async def add_on_rsi_ship(self, ctx: commands.Context, ship: str):
        await ctx.defer(ephemeral=True)
        try:
            player_id_str = str(ctx.author.id)
            if player_id_str not in self.data:
                self.data[player_id_str] = { "InGame": [], "OnRSI": []}
            self.data[player_id_str]["OnRSI"].append(ship)
            lib.save_json(self.data,lib.FLEET)
            await ctx.send(f"✅ **{ship}** a été ajouté à votre flotte **sur RSI**.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ **Erreur :** {e}", ephemeral=True)

    @commands.hybrid_command(name="fl_remove_in_game_ship", description="Retire un vaisseau de votre flotte disponible en jeu.")
    @app_commands.autocomplete(ship=ship_autocomplete)
    async def remove_in_game_ship(self, ctx: commands.Context, ship: str):
        await ctx.defer(ephemeral=True)
        try:
            player_id_str = str(ctx.author.id)
            if player_id_str not in self.data or not self.data[player_id_str].get("InGame"):
                await ctx.send(f"ℹ️ Vous n'avez aucun vaisseau dans votre flotte **en jeu**.", ephemeral=True)
            else:
                if ship not in self.data[player_id_str]["InGame"]:
                    await ctx.send(f"⚠️ Vous ne possédez pas le vaisseau **{ship}** dans votre flotte **en jeu**.", ephemeral=True)
                else:
                    self.data[player_id_str]["InGame"].remove(ship)
                    lib.save_json(self.data,lib.FLEET)
                    await ctx.send(f"🗑️ **{ship}** a été retiré de votre flotte **en jeu**.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ **Erreur :** {e}", ephemeral=True)

    @commands.hybrid_command(name="fl_remove_on_rsi_ship", description="Retire un vaisseau de votre flotte listée sur le site RSI (hangar).")
    @app_commands.autocomplete(ship=ship_autocomplete)
    async def remove_on_rsi_ship(self, ctx: commands.Context, ship: str):
        await ctx.defer(ephemeral=True)
        try:
            player_id_str = str(ctx.author.id)
            if player_id_str not in self.data or not self.data[player_id_str].get("OnRSI"):
                await ctx.send(f"ℹ️ Vous n'avez aucun vaisseau dans votre flotte **sur RSI**.", ephemeral=True)
            else:
                if ship not in self.data[player_id_str]["OnRSI"]:
                    await ctx.send(f"⚠️ Vous ne possédez pas le vaisseau **{ship}** dans votre flotte **sur RSI**.", ephemeral=True)
                else:
                    self.data[player_id_str]["OnRSI"].remove(ship)
                    lib.save_json(self.data,lib.FLEET)
                    await ctx.send(f"🗑️ **{ship}** a été retiré de votre flotte **sur RSI**.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ **Erreur :** {e}", ephemeral=True)

    @commands.hybrid_command(name="fl_get_my_fleet", description="Affiche la liste de vos vaisseaux (en jeu et sur RSI).")
    async def get_my_fleet(self, ctx: commands.Context):
        await ctx.defer(ephemeral=True)
        try:
            player_id_str = str(ctx.author.id)
            if player_id_str not in self.data or (not self.data[player_id_str].get("InGame") and not self.data[player_id_str].get("OnRSI")):
                await ctx.send(f"ℹ️ Vous n'avez aucun vaisseau enregistré.", ephemeral=True)
            else:
                msg = f"## <:Logo:1306335943568920717> Flotte de {ctx.author.display_name}\n"
                
                in_game_ships = self.data[player_id_str].get("InGame", [])
                if in_game_ships:
                    msg += "### <:LogoBlanc:1306335856532914206> Flotte en jeu\n"
                    msg += "```\n" + "\n".join(f"- {ship}" for ship in sorted(in_game_ships)) + "\n```\n"
                
                on_rsi_ships = self.data[player_id_str].get("OnRSI", [])
                if on_rsi_ships:
                    msg += "### <:rsi:778326516064321581> Flotte sur RSI\n"
                    msg += "```\n" + "\n".join(f"- {ship}" for ship in sorted(on_rsi_ships)) + "\n```\n"
                    
                await ctx.send(msg, ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ **Erreur :** {e}", ephemeral=True)
    
    async def send_ship_list(self, ctx: commands.Context, header, ship_dict):
                if not ship_dict:
                    return
                
                message_parts = []
                current_part = f"{header}```\n"
                for ship, count in sorted(ship_dict.items()):
                    line = f"- {ship} (x{count})\n"
                    if len(current_part) + len(line) > 1990: # Keep a buffer for closing backticks
                        current_part += "```"
                        message_parts.append(current_part)
                        current_part = "```\n"
                    current_part += line
                current_part += "```"
                message_parts.append(current_part)

                for part in message_parts:
                    await ctx.send(part)

    @commands.hybrid_command(name="fl_get_org_fleet", description="Affiche la liste de tous les vaisseaux de l'organisation.")
    async def get_org_fleet(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False) # Visible par tous
        try:
            all_in_game = {}
            all_on_rsi = {}

            for player_id, fleets in self.data.items():
                for ship in fleets.get("InGame", []):
                    all_in_game[ship] = all_in_game.get(ship, 0) + 1
                for ship in fleets.get("OnRSI", []):
                    all_on_rsi[ship] = all_on_rsi.get(ship, 0) + 1

            title = "## <:Logo:1306335943568920717> Flotte de la Légion Écarlate\n"
            await ctx.send(title)

            if not all_in_game and not all_on_rsi:
                await ctx.send("ℹ️ Aucun vaisseau n'a encore été enregistré dans la flotte de l'organisation.", ephemeral=True)
                return

            await self.send_ship_list(ctx, "### <:LogoBlanc:1306335856532914206> Flotte totale en jeu\n", all_in_game)
            await self.send_ship_list(ctx, "### <:rsi:778326516064321581> Flotte totale sur RSI\n", all_on_rsi)

        except Exception as e:
            await ctx.send(f"❌ **Erreur :** {e}", ephemeral=True)
    
    @commands.hybrid_command(name="fl_get_save_fleet", description="Génère et envoie le fichier de sauvegarde de la flotte pour hangar.link.")
    async def get_save_fleet(self, ctx: commands.Context):
        await ctx.defer(ephemeral=True)
        try:
            save_data = fleet_manager.create_fleet_save(self.data)
            
            if not save_data["canvasItems"]:
                await ctx.send("ℹ️ La flotte est vide. Le fichier de sauvegarde n'a pas été généré.", ephemeral=True)
                return

            lib.save_json(save_data, lib.SAVE)
            await ctx.send("✅ Voici le fichier de sauvegarde de la flotte à mettre sur [hangar.link](https://hangar.link/fleet/canvas):", file=discord.File(lib.BASE_PATH / lib.SAVE), ephemeral=True)
            
        except Exception as e:
            await ctx.send(f"❌ **Erreur :** {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    fleet_data = lib.load_json(lib.FLEET)
    if fleet_data is None:
        fleet_data = {}
    
    ship_list = fleet_manager.generate_ship_name_list()
    
    await bot.add_cog(FleetManagerCog(bot, fleet_data, ship_list))