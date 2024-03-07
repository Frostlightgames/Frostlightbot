#!/usr/bin/python3

#----------------------------------------------------
# This is Frostlightbot Version 1.0.0 [DEV]
# Created by gamexdifficulty for the Frostlight Communityserver
# Programmed in Python 3.12.2
# This code is licensed under GPLv3s
#----------------------------------------------------

import json
import discord
from data.functions.log import *
from data.functions.load_token import *

class FrostlightBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.guild_id = self.load("guild_id")

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await slash.sync(guild=discord.Object(id=self.guild_id))
            self.synced = True

        await bot.change_presence(activity=activity)
        log(INFO,"Frostlightbot online.")

    def load(self,key:str,default=None):
        try:
            with open(os.path.join("data","config.json"),"r+") as f:
                data = json.load(f)
                f.close()
                if key in data:
                    return data[key]
                else:
                    log(WARNING,f"Cannot load key {key}!")
                    return default
        
        except Exception as e:
            log(ERROR,f"Could not load {key}: {e}")

    def save(self,key:str,value:any):
        try:
            with open(os.path.join("data","config.json"),"r+") as f:
                data = json.load(f)
                data[key] = value
                json.dump(data,f)
                f.close()
                log(INFO,"Saved config file.")
        
        except Exception as e:
            log(ERROR,f"Could not load {key}: {e}")

if __name__ == "__main__":
    try:
        token = load_token()
        activity = discord.Game(name="Frostlightgames")
        bot = FrostlightBot()
        slash = discord.app_commands.CommandTree(bot)
        bot.run(token)
    except Exception as e:
        log(ERROR,f"Failed to start: {e}")
        