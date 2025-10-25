import os
import random
import discord
import datetime

from main import FrostlightBot
from data.classes.event import Event
from data.classes.logger import LOGGER
from data.classes.database import DATABASE

SWEETS_GOAL = 100
LOOT_BAG_REMAIN_TIMER = 3

class HalloweenEvent(Event):
    def __init__(self, bot:FrostlightBot) -> None:
        super().__init__(bot)
        self.lootbag_wait_time = random.randint(1,3)
        self.halloween_text_channel = None
        self.halloween_chat_category = None
        self.halloween_looter_role = None
        self.halloween_reward_role = None
        self.halloween_notification_title_text = "**Es ist Halloween und hier könnt ihr nun Süßigkeiten sammeln. Wenn ihr jedoch keine Benachrichtigungen bekommen wollt, stellt dies hier ein!**"
        self.halloween_notification_embed = None
        self.halloween_notification_view = None
        self.halloween_loot_bag_view = None
        self.halloween_last_loot_bag_message = None
        self.halloween_loot_bag_marked_for_deletion = False
        self.halloween_loot_bag_collected_list = []
        self.prepared = False

    async def check_event_time(self):

        # Check for halloween date
        if datetime.datetime.now().date().strftime("%d-%m") == "25-10":

            # Pre event checkups and preparation, the day of the event
            if datetime.datetime.now().hour >= 0 and datetime.datetime.now().hour <= 22 and self.prepared == False:
                await self.prepare()

            # Main halloween event
            if datetime.datetime.now().hour >= 3 and datetime.datetime.now().hour <= 22:
                return True
            
        return await super().check_event_time()
    
    def check_event_time_window(self):
        now = datetime.datetime.now()
        return now.date().strftime("%d-%m") == "25-10" and now.hour >= 18 and now.hour <= 22
    
    async def prepare(self):
        from data.events.halloween.lootbag.lootbag_collection_button import HalloweenLootBagButton
        from data.events.halloween.notification.notification_buttons import HalloweenNotifyYesButton, HalloweenNotifyNoButton

        await LOGGER.info("Preparing halloween event")

        # Fetching needed roles and channels
        try:
            await LOGGER.info("Fetching roles and channels")
            self.halloween_chat_category = await self.bot.guild.fetch_channel(DATABASE.get_config("halloween_chat_category"))
            self.halloween_looter_role = self.bot.guild.get_role(int(DATABASE.get_config("halloween_looter_role")))
            halloween_channels = await self.bot.guild.fetch_channels()

            # Searching for halloween text channel
            await LOGGER.info("Searching for halloween text channel and checking if it already exists")
            for channel in halloween_channels:
                if channel.category_id != None and channel.category_id == self.halloween_chat_category.id:
                    if channel.name.split("-")[1] == str(datetime.datetime.now().year):
                        self.halloween_text_channel = channel
                    else:

                        # Setting read only for other channels in halloween category
                        permission = discord.PermissionOverwrite()
                        permission.send_messages = False
                        permission.view_channel = True
                        permission.read_message_history = True
                        await channel.set_permissions(self.bot.member_role, overwrite=permission)

            # Creating new halloween channel if it does not exists
            await LOGGER.info("Creating new halloween channel if not already existent")
            if self.halloween_text_channel == None:
                permission = discord.PermissionOverwrite()
                permission.send_messages = False
                permission.read_message_history = True
                permission.view_channel = False
                self.halloween_text_channel = await self.bot.guild.create_text_channel(f"🍬halloween-{datetime.datetime.now().year}", category=self.halloween_chat_category,position=0,topic=f"Loot Kanal für das Halloween Event in {datetime.datetime.now().year}",overwrites={self.bot.member_role:permission})

            # Searching for halloween notification embed
            await LOGGER.info("Searching for halloween notification option embed and checking if it already exists")
            messages = [message async for message in self.halloween_text_channel.history(limit=10, oldest_first=True)]
            for message in messages:
                if len(message.embeds) == 1:
                    if message.embeds[0].title == self.halloween_notification_title_text:
                        self.halloween_notification_embed = message.embeds[0]
                        break

            # Searching for halloween reward role
            await LOGGER.info("Searching for halloween reward role")
            halloween_roles = await self.bot.guild.fetch_roles()
            for role in halloween_roles:
                if str(role.name).startswith("Halloween Candy Collector") and str(role.name).split(" ")[3] == str(datetime.datetime.now().year):
                    self.halloween_reward_role = role

            # Creating halloween reward role if it does not exist
            await LOGGER.info("Creating halloween reward role if it does not existent")
            if self.halloween_reward_role == None:
                self.halloween_reward_role = await self.bot.guild.create_role(name=f"Halloween Candy Collector {datetime.datetime.now().year}",color=0xe67e22)

            # Change bot avatar to halloween edition
            await LOGGER.info("Change bot avatar to halloween edition")
            with open(os.path.join("data","images","bot_avatar_halloween.png"), 'rb') as image:
                image_data = image.read()
                await self.bot.user.edit(avatar=image_data)

            # Creating persistent views
            await LOGGER.info("Creating persistent views")
            self.halloween_notification_view = discord.ui.View(timeout=None)
            self.halloween_notification_view.add_item(item=HalloweenNotifyYesButton(self))
            self.halloween_notification_view.add_item(item=HalloweenNotifyNoButton(self))
            self.bot.add_view(view=self.halloween_notification_view)
            self.halloween_loot_bag_view = discord.ui.View(timeout=None)
            self.halloween_loot_bag_view.add_item(item=HalloweenLootBagButton(self.bot,self))
            self.bot.add_view(view=self.halloween_loot_bag_view)

            # All clear check
            if self.halloween_chat_category != None and self.halloween_looter_role != None and self.halloween_text_channel != None and self.halloween_reward_role != None and self.halloween_notification_view != None and self.halloween_loot_bag_view != None:
                self.prepared = True
                await LOGGER.info("Halloween event fully prepared")

        except Exception as e:
            await LOGGER.error(f"Failed to prepare halloween event: {e}")

    async def start(self):
        await super().start()

        await LOGGER.info("Starting halloween event")

        # Unlocking halloween text channel
        await LOGGER.info("Unlocking halloween text channel")
        permission = discord.PermissionOverwrite()
        permission.send_messages = True
        permission.read_message_history = True
        permission.view_channel = False # CHANGE BACK TO TRUE
        await self.halloween_text_channel.set_permissions(self.bot.member_role, overwrite=permission)

        # Giving everybody an event role
        if not DATABASE.get_config(f"halloween_event_{datetime.datetime.now().year}_role_distribution", False):
            await LOGGER.info("Giving everybody an event role")
            for member in self.bot.get_all_members():
                await member.add_roles(self.halloween_looter_role)
            DATABASE.set_config(f"halloween_event_{datetime.datetime.now().year}_role_distribution",True)

        # Announce event start
        if not DATABASE.get_config(f"halloween_event_{datetime.datetime.now().year}_announcement_message", False):
            await LOGGER.info("Sending event start announcement")
            activity = discord.Game(name="Halloween")
            await self.bot.change_presence(activity=activity)
            embed = discord.Embed(color=0xfa5c07,title="***🎃🦇👻Happy Halloween👻🦇🎃***")
            embed.add_field(name="Link zum Event",value=self.halloween_text_channel.mention)
            await self.bot.sandbox_text_channel.send(self.bot.member_role.mention,embed=embed)
            DATABASE.set_config(f"halloween_event_{datetime.datetime.now().year}_announcement_message",True)

        # Sending notification option embed
        await LOGGER.info("Sending notification option embed")
        if self.halloween_notification_embed == None:
            embed = discord.Embed(title=self.halloween_notification_title_text, color=0xfa5c07)
            embed.add_field(name="Beschreibung:",value="Hier kannst du entscheiden, ob du Benachrichtigungen erhalten willst!")
            thumbnail = discord.File(os.path.join("data","images","halloweenbell.png"), filename='halloweenbell.png')  
            embed.set_thumbnail(url="attachment://halloweenbell.png")
            embed = await self.halloween_text_channel.send(self.halloween_looter_role.mention,file=thumbnail,embed=embed,view=self.halloween_notification_view)

        await LOGGER.info("Halloween event fully started")

    async def update(self):
        from data.events.halloween.lootbag.generate_lootbag import generate_loot_bag

        if self.halloween_last_loot_bag_message == None:
            # Count down time sub events
            self.lootbag_wait_time = max(0,self.lootbag_wait_time-1)
            
            # Lootbag event
            if self.lootbag_wait_time == 0:
                await LOGGER.info(f"Generating loot bag")
                await generate_loot_bag(self)

                # Set new time for lootbag to appear
                self.lootbag_wait_time = random.randint(2,7)
            else:
                await LOGGER.info(f"Next lootbag in {self.lootbag_wait_time} minutes")
            
        else:
            await LOGGER.info("Lootbag still present, no new lootbag will be generated")

    async def end(self):
        await super().end()

        await LOGGER.info("Ending halloween event")

        # Create a summary of the collected candy
        await LOGGER.info("Creating a summary of the collected candy")
        await self.bot.member_manager.scan_for_member()
        embed = discord.Embed(title=f'🍬Das Event ist vorbei, hier ist die auswertung🍬' , color=0xfa5c07)
        for member in self.bot.member_manager.member_list:
            if self.bot.member_manager.member_list[member].candy > 0:
                embed.add_field(name=f"{self.bot.member_manager.member_list[member].name}",value=f"{self.bot.member_manager.member_list[member].candy} 🍬", inline=False)
        embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
        await self.halloween_text_channel.send(self.halloween_looter_role.mention ,embed=embed)

        # Set halloween channel to read only
        await LOGGER.info("Setting halloween channel to read only")
        permission = discord.PermissionOverwrite()
        permission.send_messages = False
        await self.halloween_text_channel.set_permissions(self.bot.member_role, overwrite=permission)

        # Remove event role from everybody
        await LOGGER.info("Removing event role from everybody")
        for member in self.bot.get_all_members():
            await member.remove_roles(self.halloween_looter_role)

        # Resetting candy count of every member to 0
        await LOGGER.info("Resetting every members candy count to 0")
        self.bot.member_manager.scan_for_member()
        for member in self.bot.member_manager.member_list:
            self.bot.member_manager.member_list[member].candy = 0

        # Reset event variables
        await LOGGER.info("Resetting event variables")
        self.lootbag_wait_time = 0
        self.halloween_text_channel = None
        self.halloween_chat_category = None
        self.halloween_looter_role = None
        self.halloween_reward_role = None
        self.halloween_notification_embed = None
        self.halloween_notification_view = None
        self.halloween_loot_bag_view = None
        self.halloween_loot_bag_marked_for_deletion = False
        self.halloween_loot_bag_collected_list = []
        self.prepared = False

        # Change bot avatar to normal
        await LOGGER.info("Changing bot avatar to normal")
        with open(os.path.join("data","images","bot_avatar.png"), 'rb') as image:
            image_data = image.read()
            await self.bot.user.edit(avatar=image_data)

        # Reset game status
        await LOGGER.info("Resetting game status")
        activity = discord.Game(name="Frostlightgames")
        await self.bot.change_presence(activity=activity)