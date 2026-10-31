import discord
import datetime
from zoneinfo import ZoneInfo

def register_endhalloween_command(slash, bot):
    @slash.command(name="endhalloween",description="[gamex] Endet das diesjährige Halloween Event",guild=discord.Object(id=670321104866377748))
    async def endhalloween_command(interaction:discord.Integration):
        
        now = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
        timestamp = now.strftime("[%d.%m.%Y %H:%M]")

        if interaction.user.id == 465412731709816853:

            await bot.event_manager.events[0].end()

            embed = discord.Embed(title="gamexdifficulty hat das Halloween Event beendet.", color=0x000000)
            await bot.log_text_channel.send(embed=embed)

        else:
            embed = discord.Embed(title="Keine Berechtigung für diesen Befehl", color=0x262626)
            embed.set_footer(text=timestamp)
            await interaction.response.send_message(embed=embed)