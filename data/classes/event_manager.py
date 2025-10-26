import asyncio
import datetime

from main import *
from data.classes.logger import LOGGER

from data.events.halloween.halloween import  HalloweenEvent

class EventManager:
    def __init__(self,bot:FrostlightBot) -> None:
        self.bot = bot
        self.events = [
            HalloweenEvent(self.bot)
        ]

    async def update(self):
        while not self.bot.is_closed():
            try:
                for event in self.events:
                    if await event.check_event_time():
                        if not event.has_started:
                            await event.start()
                        await event.update()
                    else:
                        if event.has_started:
                            await event.end()

                await asyncio.sleep(60-datetime.datetime.now().second)
            except Exception as e:
                await LOGGER.error(f"Error while running event loops: | {e}", self.bot)