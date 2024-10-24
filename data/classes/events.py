import asyncio
import datetime

from main import FrostlightBot

class Event:
    def __init__(self,bot:FrostlightBot) -> None:
        self.bot = bot
        self.id = ""
        self.has_started = False
    
    async def check_event_time(self):

        # Inherited function for checking if an event has started or needs preparation
        return False
    
    async def start(self):

        # Inherited function for initial start logic of an event
        self.has_started = True
    
    async def update(self):

        # Inherited function for the event loop
        return True
    
    async def end(self):

        # Inherited function for the end logic of an event
        self.has_started = False
    
from data.events.halloween import HalloweenEvent

class Events:
    def __init__(self,bot:FrostlightBot) -> None:
        self.bot = bot

        # Register all events below
        self.events = [
            HalloweenEvent(self.bot)
        ]

    async def update(self):
        while not self.bot.is_closed():
            for event in self.events:

                # Executed at the start of every minute
                if await event.check_event_time():
                    if not event.has_started:
                        await event.start()
                    await event.update()
                else:
                    if event.has_started:
                        await event.end()

            await asyncio.sleep(60-datetime.datetime.now().second)