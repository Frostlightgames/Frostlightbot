import discord
import datetime

from data.events.halloween.halloween import *

class HalloweenEventTutorialButton(discord.ui.Button):
    def __init__(self,event: HalloweenEvent):
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(style=discord.ButtonStyle.blurple, label="Event Tutorial",custom_id=f"HalloweenEventTutorialButton{datetime.datetime.now().year}")

    async def callback(self, interaction: discord.Interaction):
        if self.event.check_event_time_window() and self.year == datetime.datetime.now().year:
            with open(os.path.join("data","events","halloween","tutorial","tutorial_message.md"),"r",encoding="utf-8") as f:
                content = f.read()
                f.close()
            await interaction.response.send_message(f"{content.replace("!YEAR!",str(datetime.datetime.now().year)).replace("!BAG_TIMER!",str(LOOT_BAG_REMAIN_TIMER))}",ephemeral=True)
        else:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            await interaction.response.send_message(embed=embed,ephemeral=True)