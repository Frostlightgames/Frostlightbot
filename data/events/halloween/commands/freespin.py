import discord
import datetime
from zoneinfo import ZoneInfo
from data.classes.database import DATABASE

def register_freespin_command(slash, bot):
    @slash.command(name="freespin",description="[gamex] Vergibt gratis Spukraddrehs",guild=discord.Object(id=670321104866377748))
    async def free_spin_command(interaction:discord.Integration, name:str="", amount:int=1):
        
        now = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
        timestamp = now.strftime("[%d.%m.%Y %H:%M]")

        if interaction.user.id == 465412731709816853:

            DATABASE.set_config(f"halloween_free_spins_{name}",str(amount))

            member = bot.member_manager.get(name=name)
            await bot.get_user(member.uid).send(f"Dir wurden {amount} gratis Spukraddrehs für das Halloween Event {now.year} geschenkt.")

            embed = discord.Embed(title="Gratis Spukraddrehs", color=0x000000)
            embed.add_field(name=f"{amount} Gratis Spukraddrehs wurden an {name}",value=timestamp,inline=True)
            await bot.log_text_channel.send(embed=embed)

            embed = discord.Embed(title="Gratis Spukraddrehs wurden vergeben.", color=0x262626)
            embed.set_footer(text=timestamp)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Keine Berechtigung für diesen Befehl", color=0x262626)
            embed.set_footer(text=timestamp)
            await interaction.response.send_message(embed=embed)