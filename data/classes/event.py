from main import FrostlightBot

class Event:
    def __init__(self,bot:FrostlightBot):
        self.bot = bot
        self.id = ""
        self.has_started = False

    async def check_time(self): ...
    async def prepare(self): ...
    async def start(self):
        self.has_started = True
    async def end(self):
        self.has_started = False
    async def update(self): ...