import asyncio
import datetime

from main import FrostlightBot

class Event:
    def __init__(self,bot:FrostlightBot) -> None:
        self.bot = bot
        self.id = ""
        self.has_started = False
    
    async def check_event_time(self):
        return False
    
    async def start(self):
        self.has_started = True
    
    async def update(self):
        return True
    
    async def end(self):
        self.has_started = False
    
from data.events.halloween import HalloweenEvent

class Events:
    def __init__(self,bot:FrostlightBot) -> None:
        self.bot = bot
        self.events = [
            HalloweenEvent(self.bot)
        ]

    async def update(self):
        while not self.bot.is_closed():
            for event in self.events:
                if await event.check_event_time():
                    if not event.has_started:
                        await event.start()
                    await event.update()
                else:
                    if event.has_started:
                        await event.end()

            await asyncio.sleep(60-datetime.datetime.now().second)