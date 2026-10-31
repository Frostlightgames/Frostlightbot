import discord
import datetime

from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING
from discord.ext import commands
from data.classes.database import DATABASE

if TYPE_CHECKING:
    from main import FrostlightBot

class HalloweenCogInteractionListener(commands.Cog):
    def __init__(self, bot: FrostlightBot):
        self.bot = bot

        self.COOLDOWN = 3
        self.INTERACTIONS_PER_CANDY = 10

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        valid_text = len(message.content.strip()) >= 10 and " " in message.content
        valid_media = len(message.attachments) > 0

        if not valid_text and not valid_media:
            return
        
        if not self.bot.event_manager.events[0].check_event_time_window():
            return

        uid = str(message.author.id)
        now = int(datetime.datetime.now(ZoneInfo("Europe/Berlin")).timestamp())

        cooldown_key = f"halloween_event_2026_{uid}_last_interaction"
        last_interaction = int(DATABASE.get_config(cooldown_key, 0))

        if now - last_interaction < self.COOLDOWN:
            return
        
        interactions = int(DATABASE.get_config(f"halloween_event_2026_{uid}_interactions", 0)) + 1
        
        if interactions >= self.INTERACTIONS_PER_CANDY:
            member = self.bot.member_manager.get(int(uid))

            if member is not None and member.candy < 90:
                member.candy += 1

            interactions = 0

        DATABASE.set_config(f"halloween_event_2026_{uid}_interactions", interactions)
        DATABASE.set_config(cooldown_key, now)

async def setup_halloween_interaction_cog(bot):
    listener = HalloweenCogInteractionListener(bot)
    bot.add_listener(listener.on_message, "on_message")