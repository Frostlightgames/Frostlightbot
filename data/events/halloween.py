import asyncio
import random
import discord
import datetime

from main import FrostlightBot
from data.classes.events import Event
from data.functions.log import *

class HalloweenNotifyButton(discord.ui.Button):
    def __init__(self,bot:FrostlightBot,button_type,event):
        self.bot = bot
        self.event = event
        self.button_type = button_type
        if button_type == 0:
            super().__init__(style=discord.ButtonStyle.green, label="Benachrichtigungen")
        if button_type == 1:
            super().__init__(style=discord.ButtonStyle.red, label="Keine Benachrichtigungen")

    async def callback(self, interaction: discord.Interaction):
        if self.button_type == 0:
            embed = discord.Embed(title=f"Du erhältst nun Loot Benachrichtigungen!" , color=0x32a852)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await interaction.user.add_roles(self.event.halloween_looter_role)
        
        if self.button_type == 1:
            embed = discord.Embed(title=f"Du erhältst keine Loot Benachrichtigungen mehr!" , color=0xa83232)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await interaction.user.remove_roles(self.event.halloween_looter_role)

class HalloweenLootBagButton(discord.ui.Button):
    def __init__(self,bot:FrostlightBot):
        self.bot = bot

        super().__init__(style=discord.ButtonStyle.blurple, label="Halloween Snacks")

    async def callback(self, interaction: discord.Interaction):
        try:
            user = interaction.user.name
            if user not in self.bot.loot_coins:
                self.bot.loot_coins[user] = [0,False]
            sweets = random.randint(3,8)
            self.bot.loot_coins[user][0] += sweets
            await self.bot.save()
            if self.bot.loot_coins[user][0] >= 50 and not self.bot.loot_coins[user][1]:
                self.bot.loot_coins[user][1] = True
                await self.bot.save()
                await interaction.user.add_roles(self.bot.reward_role)
                embed = discord.Embed(title=f'👻🎃🦇 {interaction.user.name} hat das Süßigkeiten Ziel erreicht! 🦇🎃👻' , color=0xbfa945)
                embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                info_message = await self.bot.loot_channel.send(embed=embed)
            else:
                embed = discord.Embed(title=f'🍬 {interaction.user.name} hat {sweets} Süßigkeiten gesammelt 🍬' , color=0xbfa945)
                embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                info_message = await self.bot.loot_channel.send(embed=embed)

            if self.bot.loot_coins[user][1]:
                embed = discord.Embed(title=f"Du hast bereits {self.bot.loot_coins[user][0]} Süßigkeiten gesammelt, aber hör nicht auf mit sammeln! 🍬" , color=0xbfa945)
                embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                await interaction.response.send_message(embed=embed,ephemeral=True)
            else:
                embed = discord.Embed(title=f"Sammel Status: {self.bot.loot_coins[user][0]}|{'#'*int(20*min(self.bot.loot_coins[user][0]/50,1))}{'-'*(20-int(20*min(self.bot.loot_coins[user][0]/50,1)))}|50" , color=0xbfa945)
                embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                await interaction.response.send_message(embed=embed,ephemeral=True)

            await interaction.message.delete()
            self.bot.free_box = True
            await asyncio.sleep(30)
            await info_message.delete()
        except Exception as e:
            print(e)

class HalloweenEvent(Event):
    def __init__(self, bot:FrostlightBot) -> None:
        super().__init__(bot)
        self.lootbag_wait_time = 0
        self.halloween_text_channel = None
        self.halloween_chat_category = None
        self.halloween_looter_role = None
        self.prepared = False

    async def check_event_time(self):

        # Check for halloween date
        if datetime.datetime.now().date().strftime("%d-%m") == "31-10":

            # Pre event checkups and preparation, 1 hour before the event
            if datetime.datetime.now().hour >= 17 and datetime.datetime.now().hour <= 22 and self.prepared == False:
                await self.prepare()

            # Main halloween event
            if datetime.datetime.now().hour >= 18 and datetime.datetime.now().hour <= 22:
                return True
            
        return await super().check_event_time()
    
    async def prepare(self):
        # Fetching needed roles and channels
        try:
            self.halloween_chat_category = await self.bot.guild.fetch_channel(self.bot.database.get_config("halloween_chat_category",1168661170920620172))
            self.halloween_looter_role = self.bot.guild.get_role(self.bot.database.get_config("halloween_looter_role",1168660197468819487))
            halloween_channels = await self.bot.guild.fetch_channels()

            # Searching for halloween text channel
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

            # Creating new halloween channel if it dont exists
            if self.halloween_text_channel == None:
                permission = discord.PermissionOverwrite()
                permission.send_messages = False
                permission.read_message_history = True
                permission.view_channel = False
                self.halloween_text_channel = await self.bot.guild.create_text_channel(f"🍬halloween-{datetime.datetime.now().year}", category=self.halloween_chat_category,position=0,topic=f"Loot Kanal für das Halloween Event in {datetime.datetime.now().year}",overwrites={self.bot.member_role:permission})

            # All clear check
            if self.halloween_chat_category != None and self.halloween_looter_role != None and self.halloween_text_channel != None:
                self.prepared = True

        except Exception as e:
            log(ERROR,f"Failed to prepare Halloween Event: {e}")

    async def start(self):
        await super().start()

        # Announce event start
        activity = discord.Game(name="Halloween")
        await self.bot.change_presence(activity=activity)
        embed = discord.Embed(color=0xFC4C02,title="***🎃🦇👻Happy Halloween👻🦇🎃***")
        # await self.bot.general_text_channel.send(self.bot.member_role.mention,embed=embed)

        # Unlocking halloween text channel
        permission = discord.PermissionOverwrite()
        permission.send_messages = True
        permission.read_message_history = True
        permission.view_channel = True
        await self.halloween_text_channel.set_permissions(self.bot.member_role, overwrite=permission)

        # Giving everybody an event role
        for member in self.bot.get_all_members():
            await member.add_roles(self.halloween_looter_role)

        # Sending notification option embed
        self.halloween_notification_view = discord.ui.View(timeout=None)
        embed = discord.Embed(title="Es ist Halloween und hier könnt ihr nun Süßigkeiten sammeln. Wenn ihr jedoch keine Benachrichtigungen bekommen wollt, stellt dies hier ein!", color=0xfa5c07)
        embed.add_field(name="Beschreibung:",value="Hier kannst du entscheiden, ob du Benachrichtigungen erhalten willst!")
        self.halloween_notification_view.add_item(item=HalloweenNotifyButton(self,0,self))
        self.halloween_notification_view.add_item(item=HalloweenNotifyButton(self,1,self))
        self.bot.add_view(self.halloween_notification_view)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/548636271107637251/1168692612224516116/bell.png?ex=6707ba10&is=67066890&hm=e43991fc9f86761ca9365e2fb0d5e61e223c22ac09864f37555756950646432c&")
        embed = await self.halloween_text_channel.send(self.halloween_looter_role.mention,embed=embed,view=self.halloween_notification_view)

    async def update(self):

        # Count down time until new lootbag
        self.lootbag_wait_time = max(0,self.lootbag_wait_time-1)
        if self.lootbag_wait_time == 0:
            self.generate_lootbag()

            # Set new time for lootbag to appear
            self.lootbag_wait_time = random.randint(2,10)

    async def generate_lootbag(self):
        button_view = discord.ui.View(timeout=None)
        embed = discord.Embed(title="Eine Süßigkeitenbox ist erschienen", color=0xfa5c07)
        embed.add_field(name="Beschreibung:",value="Sammle 100 Süßigkeiten um eine spezielle Rolle zu erhalten!")
        button_view.add_item(item=HalloweenLootBagButton(self))
        self.bot.add_view(button_view)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/548636271107637251/1168692081821220934/candybag.png?ex=6707b991&is=67066811&hm=6abb4d2454340b1de391219dc6eda2d6716e518c0b9cbcd13572172066b0c428&")
        embed = await self.halloween_text_channel.send(self.halloween_looter_role.mention,embed=embed,view=button_view)

    async def end(self):
        await super().end()

        # Set halloween channel to read only
        permission = discord.PermissionOverwrite()
        permission.send_messages = False
        await self.halloween_text_channel.set_permissions(self.bot.member_role, overwrite=permission)

        # Remove event role from everybody
        for member in self.bot.get_all_members():
            await member.remove_roles(self.halloween_looter_role)

        # Reset game status
        activity = discord.Game(name="Frostlightgames")
        await self.bot.change_presence(activity=activity)