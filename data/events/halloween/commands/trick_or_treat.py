import discord
import datetime
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING
from data.classes.database import DATABASE
from data.events.halloween.trick_or_treat.trick_or_treat_modal import TrickOrTreatModal

if TYPE_CHECKING:
    from main import FrostlightBot

def register_trick_or_treat_command(slash, bot: FrostlightBot):
    @slash.command(name="süßes-oder-saures",description="[Halloween] Klau jetzt die Süßigkeiten der anderen🤫",guild=discord.Object(id=670321104866377748))
    async def trick_or_treat_command(interaction:discord.Integration):
        
        if not bot.event_manager.events[0].check_event_time_window():
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y • %H:%M"))
            return await interaction.response.send_message(embed=embed,ephemeral=True)
        
        if datetime.datetime.fromisoformat(DATABASE.get_config(f"halloween_event_2026_{interaction.user.id}_trick_or_treat_command_cooldown", "2000-01-01T00:00:00")) <= datetime.datetime.now(ZoneInfo("Europe/Berlin")): 
            await interaction.response.send_modal(TrickOrTreatModal(bot, bot.member_manager.get(interaction.user.id)))
        else:
            embed = discord.Embed(title=f"Du kannst diesen Befehl erst wieder <t:{int(datetime.datetime.fromisoformat(DATABASE.get_config(f"halloween_event_2026_{interaction.user.id}_trick_or_treat_command_cooldown", 0)).timestamp())}:R> ausführen.", color=0x262626)
            embed.set_footer(text=datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y • %H:%M"))
            return await interaction.response.send_message(embed=embed,ephemeral=True)