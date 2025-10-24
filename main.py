import os
import sys
import discord
import traceback

from pathlib import Path

from data.init import init
from data.classes.logger import LOGGER
from data.classes.database import DATABASE
from data.classes.event_manager import *
from data.classes.member_manager import *

init()

class FrostlightBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.guild_id = DATABASE.get_config("guild_id")

        self.event_manager = None
        self.member_manager = None
        
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await slash.sync(guild=discord.Object(id=self.guild_id))
            self.synced = True

        self.guild = await self.fetch_guild(self.guild_id)
        self.general_text_channel = await self.guild.fetch_channel(DATABASE.get_config("main_channel_id"))
        self.sandbox_text_channel = await self.guild.fetch_channel(DATABASE.get_config("sandbox_channel_id"))
        self.log_text_channel = await self.guild.fetch_channel(DATABASE.get_config("log_channel_id"))
        print(DATABASE.get_config("main_member_role_id"))
        self.member_role = self.guild.get_role(int(DATABASE.get_config("main_member_role_id")))
        print(self.guild.get_role(1135178386906562580),self.member_role)

        self.event_manager = EventManager(self)
        self.member_manager = MemberManager(self)

        await LOGGER.info("Frostlightbot Online", self)

        embed = discord.Embed(color=0xfa5c07,title="***Test***")
        embed.add_field(name="Link zum Event",value=self.sandbox_text_channel.mention)
        thumbnail = discord.File(os.path.join("data","images","halloweenbell.png"), filename='halloweenbell.png')  
        embed.set_thumbnail(url="attachment://halloweenbell.png")
        await self.sandbox_text_channel.send(self.member_role.mention,embed=embed,file=thumbnail)

        embed = discord.Embed(color=0xfa5c07,title="***Test***")
        embed.add_field(name="Link zum Event",value=self.sandbox_text_channel.mention)
        thumbnail = discord.File(os.path.join("data","images","candybag.png"), filename='candybag.png')  
        embed.set_thumbnail(url="attachment://candybag.png")
        await self.sandbox_text_channel.send(self.member_role.mention,embed=embed,file=thumbnail)

token = os.getenv("TOKEN")
activity = discord.Game(name="Frostlightgames")
bot = FrostlightBot()
slash = discord.app_commands.CommandTree(bot)

@slash.command(name="stop",description="[Moderation] Stopt den Frostlightbot",guild=discord.Object(id=670321104866377748))
async def stop_command(interaction:discord.Integration):
    admin = False
    for role in interaction.user.roles:
        if role.id in [1010668967913861192]:
            admin = True
            break

    now = datetime.datetime.now()
    timestamp = now.strftime("[%d.%m.%Y %H:%M]")

    if admin:
        embed = discord.Embed(title="Bot Stop", color=0x000000)
        embed.add_field(name=f"Gestoppt von {interaction.user.name}",value=timestamp,inline=True)
        await bot.log_text_channel.send(embed=embed)

        embed = discord.Embed(title="Frostlightbot wurde gestoppt", color=0x262626)
        embed.set_footer(text=timestamp)
        await interaction.response.send_message(embed=embed)

        await bot.close()
    else:
        embed = discord.Embed(title="Keine Berechtigung für diesen Befehl", color=0x262626)
        embed.set_footer(text=timestamp)
        await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    try:
        bot.run(token)
                
    except Exception as e:
        ex_type, ex_value, ex_traceback = sys.exc_info()
        trace = traceback.extract_tb(ex_traceback)[-1]
        filename = Path(trace.filename).name
        line_number = trace.lineno
        function = trace.name
        error_message = (f"Exception: {ex_type.__name__} | {ex_value} | File: {filename}, Line: {line_number}, Function: {function} | Failed to start")
        LOGGER._log("ERROR", error_message)
