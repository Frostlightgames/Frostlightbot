#!/usr/bin/python3

#----------------------------------------------------
# This is Frostlightbot Version 10.0.0 [DEV]
# Created by gamexdifficulty for the Frostlight Communityserver
# Programmed in Python 3.13.0
# This code is licensed under GPLv3s
#----------------------------------------------------

import discord
from data.classes.events import *
from data.classes.database import *
from data.classes.member import *
from data.functions.log import *

class FrostlightBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.database = Database(self)
        self.guild_id = self.database.get_config("guild_id",670321104866377748)
        
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await slash.sync(guild=discord.Object(id=self.guild_id))
            self.synced = True

        self.guild = await self.fetch_guild(self.guild_id)
        self.general_text_channel = await self.guild.fetch_channel(self.database.get_config("main_channel_id",970560114115358730))
        self.log_text_channel = await self.guild.fetch_channel(self.database.get_config("log_channel_id",1006678596846354442))
        self.member_role = self.guild.get_role(self.database.get_config("main_member_role_id",1135178386906562580))

        self.member_manager = MemberManager(self)
        await self.member_manager.check()
        self.events = Events(self)

        await bot.change_presence(activity=activity)
        log(INFO,"Frostlightbot online.")
        self.event_updater = self.loop.create_task(self.events.update())


if __name__ == "__main__":
    try:
        token = ""
        activity = discord.Game(name="Frostlightgames")
        bot = FrostlightBot()
        slash = discord.app_commands.CommandTree(bot)
        bot.run(token)
    except Exception as e:
        log(ERROR,f"Failed to start: {e}")