import discord
import datetime

from data.events.halloween.halloween import *

class HalloweenNotifyYesButton(discord.ui.Button):
    def __init__(self,event: HalloweenEvent):
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(style=discord.ButtonStyle.green, label="Benachrichtigungen",custom_id=f"HalloweenNotifyButtonYes{datetime.datetime.now().year}")

    async def callback(self, interaction: discord.Interaction):
        if self.event.check_event_time_window() and self.year == datetime.datetime.now().year:
            embed = discord.Embed(title=f"Du erhältst nun Loot Benachrichtigungen!" , color=0x32a852)
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await interaction.user.add_roles(self.event.halloween_looter_role)
        else:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            await interaction.response.send_message(embed=embed,ephemeral=True)

class HalloweenNotifyNoButton(discord.ui.Button):
    def __init__(self,event: HalloweenEvent):
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(style=discord.ButtonStyle.red, label="Keine Benachrichtigungen",custom_id=f"HalloweenNotifyButtonNo{datetime.datetime.now().year}")

    async def callback(self, interaction: discord.Interaction):
        if self.event.check_event_time_window() and self.year == datetime.datetime.now().year:
            embed = discord.Embed(title=f"Du erhältst keine Loot Benachrichtigungen mehr!" , color=0xa83232)
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await interaction.user.remove_roles(self.event.halloween_looter_role)
        else:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            await interaction.response.send_message(embed=embed,ephemeral=True)