import os
import sys
import discord
import datetime
import traceback

from pathlib import Path

from data.init import init
from data.classes.logger import LOGGER
from data.classes.database import DATABASE
from data.classes.event_manager import *
from data.classes.member_manager import *

from data.commands.stop import register_stop_command
from data.events.halloween.commands.freespin import register_freespin_command
from data.events.halloween.commands.endhalloween import register_endhalloween_command
from data.events.halloween.commands.trick_or_treat import register_trick_or_treat_command

from data.events.halloween.cogs.interaction_listener import HalloweenCogInteractionListener

init()

class FrostlightBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.guild_id = DATABASE.get_config("guild_id")

        self.event_manager = None
        self.member_manager = None
        
        self.halloween_listener = HalloweenCogInteractionListener(self)
        
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await slash.sync(guild=discord.Object(id=self.guild_id))
            self.synced = True
        
        self.guild = await self.fetch_guild(self.guild_id)
        self.general_text_channel = await self.guild.fetch_channel(DATABASE.get_config("main_channel_id"))
        self.sandbox_text_channel = await self.guild.fetch_channel(DATABASE.get_config("sandbox_channel_id"))
        self.log_text_channel = await self.guild.fetch_channel(DATABASE.get_config("log_channel_id"))
        self.member_role = self.guild.get_role(int(DATABASE.get_config("main_member_role_id")))

        self.event_manager = EventManager(self)
        self.member_manager = MemberManager(self)

        await bot.change_presence(activity=activity)
        await LOGGER.info("Frostlightbot Online", self)

        self.event_updater = self.loop.create_task(self.event_manager.update())
        
    async def on_message(self, message: discord.Message):
        await self.halloween_listener.on_message(message)

token = os.getenv("TOKEN")
activity = discord.Game(name="Frostlightgames")
bot = FrostlightBot()
slash = discord.app_commands.CommandTree(bot)

# Default commands
register_stop_command(slash, bot)

# Halloween commands
register_freespin_command(slash, bot)
register_endhalloween_command(slash, bot)
register_trick_or_treat_command(slash, bot)

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
