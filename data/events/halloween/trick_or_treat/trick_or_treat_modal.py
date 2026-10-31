import random
import discord
import datetime
from typing import TYPE_CHECKING
from data.classes.logger import LOGGER
from data.classes.database import DATABASE
from data.classes.member import Member
from data.events.halloween.halloween import SWEETS_GOAL

if TYPE_CHECKING:
    from main import FrostlightBot

class TrickOrTreatModal(discord.ui.Modal, title="Süßes oder Saures"):
    def __init__(self, bot: FrostlightBot, member: Member):
        super().__init__(timeout=0)
        self.bot = bot
        self.member = member
        self.steal_member_list = []
    
        bot.member_manager.scan_for_member()
        for member in bot.member_manager.member_list:
            if bot.member_manager.member_list[member].uid == self.member.uid:
                continue
            
            if bot.member_manager.member_list[member].uid == DATABASE.get_config(f"halloween_event_2026_{self.member.uid}_trick_or_treat_last_steal", ""):
                continue
            
            if datetime.datetime.fromisoformat(DATABASE.get_config(f"halloween_event_2026_{bot.member_manager.member_list[member].uid}_trick_or_treat_steal_cooldown", "2000-01-01T00:00:00")) > datetime.datetime.now():
                continue
            
            if bot.member_manager.member_list[member].candy >= 5:
                self.steal_member_list.append([bot.member_manager.member_list[member].uid,bot.member_manager.member_list[member].name])
        
        options = [discord.SelectOption(label=member[1], value=member[0]) for member in self.steal_member_list]
        self.member_select = discord.ui.Select(placeholder="Wähle eine Person aus", options=options, min_values=1, max_values=1)
        self.add_item(discord.ui.Label(text="Spieler", description="Wähle eine Person aus, von dem du Süßigkeiten stehlen möchtest.", component=self.member_select))

    async def on_submit(self, interaction: discord.Interaction):
        selected_member = self.bot.member_manager.get(int(self.member_select.values[0]))
        stealer_member = self.bot.member_manager.get(interaction.user.id)
        stolen_candy = random.randint(2,5)
        
        if selected_member.uid == stealer_member.uid:
            return await self.error(interaction, "Du kannst dich nicht selber beklauen 👻")
        
        if selected_member.uid == DATABASE.get_config(f"halloween_event_2026_{interaction.user.id}_trick_or_treat_last_steal", ""):
            return await self.error(interaction, "Du hast dein Ziel bereits zuletzt beklaut 👻")
        
        if datetime.datetime.fromisoformat(DATABASE.get_config(f"halloween_event_2026_{stealer_member.uid}_trick_or_treat_command_cooldown", "2000-01-01T00:00:00")) > datetime.datetime.now():
            return await self.error(interaction, f"Du kannst diesen Befehl erst wieder <t:{int(datetime.datetime.fromisoformat(DATABASE.get_config(f"halloween_event_2026_{interaction.user.id}_trick_or_treat_command_cooldown", "2000-01-01T00:00:00")).timestamp())}:R> ausführen 👻")
        
        if selected_member.candy < 5:
            return await self.error(interaction, "Dein Ziel hat zu wenig Süßigkeiten zum abgeben 👻")
        
        if selected_member.candy >= SWEETS_GOAL:
            selected_member.candy = max(SWEETS_GOAL,selected_member.candy - stolen_candy)
        else:
            selected_member.candy = max(0,selected_member.candy - stolen_candy)
            
        DATABASE.set_config(f"halloween_event_2026_{selected_member.uid}_trick_or_treat_steal_cooldown", datetime.datetime.now()+datetime.timedelta(minutes=15))
        
        old_candy_amount = stealer_member.candy
        stealer_member.candy += stolen_candy
        DATABASE.set_config(f"halloween_event_2026_{stealer_member.uid}_trick_or_treat_command_cooldown", datetime.datetime.now()+datetime.timedelta(minutes=30))
        DATABASE.set_config(f"halloween_event_2026_{stealer_member.uid}_trick_or_treat_last_steal", selected_member.uid)
        
        if old_candy_amount < SWEETS_GOAL and old_candy_amount + stolen_candy >= SWEETS_GOAL:
            # Reached Goal
            embed = discord.Embed(title=f'👻🎃🦇 **{interaction.user.name} hat das Süßigkeiten Ziel erreicht!** 🦇🎃👻' , color=0xfa5c07)
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            await self.bot.event_manager.events[0].halloween_text_channel.send(embed=embed)
            await interaction.response.defer()
        else:
            # Collection information
            progress_ratio = min(stealer_member.candy / SWEETS_GOAL, 1)
            filled = int(15 * progress_ratio)
            bar = f"{'🟧' * filled}{'⬛' * (15 - filled)}"
            percent = int(progress_ratio * 100)
                    
            embed = discord.Embed(title=f'🦇🎃👻 **{stealer_member.name} hat {stolen_candy} Süßigkeiten von {selected_member.name} geklaut!** 🦇🎃👻' , color=0xfa5c07)
            embed.description = f"""
                {selected_member.name} klau sie dir zurück!
                **Sammelstatus:** `{stealer_member.candy}/{SWEETS_GOAL}`
                `{bar}` {percent}%"""
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            await self.bot.event_manager.events[0].halloween_text_channel.send(embed=embed, delete_after=5*60)
            await interaction.response.defer()
    
    async def error(self, interaction: discord.Interaction, message: str):
        embed = discord.Embed(title=message, color=0x262626)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        return await interaction.response.send_message(embed=embed,ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await self.error(interaction,"Es gab einen Fehler 👻")
        await LOGGER.error(f"Error in TrickOrTreatModal: {error}")