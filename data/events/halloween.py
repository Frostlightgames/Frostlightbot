import asyncio
import random
import discord
import datetime

from main import FrostlightBot
from data.classes.events import Event
from data.functions.log import *

SWEETS_GOAL = 100
CANDY_STEAL_THRESHOLD = 20
COIN_STEAL_THRESHOLD = 5

class HalloweenNotifyYesButton(discord.ui.Button):
    def __init__(self,event):
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(style=discord.ButtonStyle.green, label="Benachrichtigungen",custom_id=f"HalloweenNotifyButtonYes{datetime.datetime.now().year}")

    async def callback(self, interaction: discord.Interaction):
        if self.year == datetime.datetime.now().year and datetime.datetime.now().date().strftime("%d-%m") == "31-10" and datetime.datetime.now().hour >= 18 and datetime.datetime.now().hour <= 22:
            embed = discord.Embed(title=f"Du erhältst nun Loot Benachrichtigungen!" , color=0x32a852)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await interaction.user.add_roles(self.event.halloween_looter_role)
        else:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)

class HalloweenNotifyNoButton(discord.ui.Button):
    def __init__(self,event):
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(style=discord.ButtonStyle.red, label="Keine Benachrichtigungen",custom_id=f"HalloweenNotifyButtonNo{datetime.datetime.now().year}")

    async def callback(self, interaction: discord.Interaction):
        if self.year == datetime.datetime.now().year and datetime.datetime.now().date().strftime("%d-%m") == "31-10" and datetime.datetime.now().hour >= 18 and datetime.datetime.now().hour <= 22:
            embed = discord.Embed(title=f"Du erhältst keine Loot Benachrichtigungen mehr!" , color=0xa83232)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await interaction.user.remove_roles(self.event.halloween_looter_role)
        else:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)

class HalloweenLootBagButton(discord.ui.Button):
    def __init__(self,bot:FrostlightBot,event):
        self.bot = bot
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(style=discord.ButtonStyle.blurple, label="Halloween Snacks",custom_id=f"HalloweenLootBagButton{datetime.datetime.now().year}")

    async def callback(self, interaction: discord.Interaction):

        if self.year == datetime.datetime.now().year and datetime.datetime.now().date().strftime("%d-%m") == "31-10" and datetime.datetime.now().hour >= 18 and datetime.datetime.now().hour <= 22:
            # Deleting lootbag message
            try:
                await interaction.message.delete()
            except Exception as e:
                log(WARNING,f"Failed to delete lootbag message: {e}")

            try:

                # Calculate reward
                candy = random.randint(3,10)
                coins = random.randint(2,5)

                # Applying reward
                await self.bot.member_manager.check()
                member = self.bot.member_manager.find(interaction.user)
                member.candy += candy
                member.coins += coins
                self.bot.member_manager.save(interaction.user)

                if member.candy >= SWEETS_GOAL and member.candy-candy < SWEETS_GOAL:

                    # Sweets goal reached
                    await interaction.user.add_roles(self.event.halloween_reward_role)
                    embed = discord.Embed(title=f'👻🎃🦇 **{interaction.user.name} hat das Süßigkeiten Ziel erreicht!** 🦇🎃👻' , color=0xfa5c07)
                    embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                    await self.event.halloween_text_channel.send(embed=embed)
                elif member.candy < SWEETS_GOAL:

                    # Sweets goal not yet reached
                    embed = discord.Embed(title=f'🍬 {interaction.user.name} hat einen Lootbag geöffnet 🍬' , color=0xfa5c07)
                    embed.add_field(name="Beschreibung:",value=f"{interaction.user.name} hat darin Süßigkeiten und Münzen gefunden!")
                    embed.add_field(name="Süßigkeiten:",value=f"**{candy}** 🍬")
                    embed.add_field(name="Münzen:",value=f"**{coins}** <a:frostlightcoin:857720879089975326>")
                    embed.add_field(name="Sammelstatus:",value=f"{member.candy} |{'#'*int(20*min(member.candy/SWEETS_GOAL,1))}{'-'*(20-int(20*min(member.candy/SWEETS_GOAL,1)))}| {SWEETS_GOAL}")
                    embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                    info_message = await self.event.halloween_text_channel.send(embed=embed)
                    await asyncio.sleep(60)

                    # Deleting messages to not use much space
                    try:
                        await info_message.delete()
                    except Exception as e:
                        log(WARNING,f"Failed to delete collection info message: {e}")
                else:

                    # Sweets goal already reached
                    embed = discord.Embed(title=f"Du hast bereits {member.candy} Süßigkeiten gesammelt, aber hör nicht auf mit sammeln! 🍬" , color=0xfa5c07)
                    embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                    await interaction.response.send_message(embed=embed,ephemeral=True)

            except Exception as e:
                log(ERROR,f"Failed to open Lootbag: {e}")
        else:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)

class HalloweenStealButton(discord.ui.Button):
    def __init__(self,event):
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(style=discord.ButtonStyle.green, label=f"{self.event.steal["candy"]} Süßigkeiten abgeben")

    async def callback(self, interaction: discord.Interaction):
        if self.year == datetime.datetime.now().year and datetime.datetime.now().date().strftime("%d-%m") == "31-10" and datetime.datetime.now().hour >= 18 and datetime.datetime.now().hour <= 22:
            try:

                # Get member and subtract candy
                await self.event.bot.member_manager.check()
                if interaction.user.id == self.event.steal["member"]:
                    for member in self.event.bot.member_manager.member_list:
                        if member.id == self.event.steal["member"]:
                            member.candy = max(0,member.candy-self.event.steal["candy"])
                            self.event.bot.member_manager.save(member)

                # Post ok message
                embed = discord.Embed(title=f"🍬Du hast {self.event.steal["candy"]} Süßigkeiten an den Halloweenbot abgeben" , color=0xfa5c07)
                embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                await interaction.response.send_message(embed=embed,ephemeral=True)

                # Deleting messages to not use much space
                try:
                    await self.event.steal["embed"].delete()
                except Exception as e:
                    log(WARNING,f"Failed to delete steal info message: {e}")

                self.event.steal = {"timer":0,"member":None,"candy":0,"embed":None}
            except Exception as e:
                log(ERROR,f"Failed to pay candy: {e}")
        else:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0x32a852)
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            await interaction.response.send_message(embed=embed,ephemeral=True)

class HalloweenEvent(Event):
    def __init__(self, bot:FrostlightBot) -> None:
        super().__init__(bot)
        self.lootbag_wait_time = random.randint(1,3)
        self.candy_steal_timer = random.randint(20,40)
        self.steal_timeout = {}
        self.steal = {"timer":0,"member":None,"candy":0,"embed":None}
        self.halloween_text_channel = None
        self.halloween_chat_category = None
        self.halloween_looter_role = None
        self.halloween_reward_role = None
        self.halloween_notification_title_text = "**Es ist Halloween und hier könnt ihr nun Süßigkeiten sammeln. Wenn ihr jedoch keine Benachrichtigungen bekommen wollt, stellt dies hier ein!**"
        self.halloween_notification_embed = None
        self.halloween_notification_view = None
        self.halloween_loot_bag_view = None
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

            # Creating new halloween channel if it does not exists
            if self.halloween_text_channel == None:
                permission = discord.PermissionOverwrite()
                permission.send_messages = False
                permission.read_message_history = True
                permission.view_channel = False
                self.halloween_text_channel = await self.bot.guild.create_text_channel(f"🍬halloween-{datetime.datetime.now().year}", category=self.halloween_chat_category,position=0,topic=f"Loot Kanal für das Halloween Event in {datetime.datetime.now().year}",overwrites={self.bot.member_role:permission})

            # Searching for halloween notification embed
            messages = [message async for message in self.halloween_text_channel.history(limit=10, oldest_first=True)]
            for message in messages:
                if len(message.embeds) == 1:
                    if message.embeds[0].title == self.halloween_notification_title_text:
                        self.halloween_notification_embed = message.embeds[0]
                        break

            # Searching for halloween reward role
            halloween_roles = await self.bot.guild.fetch_roles()
            for role in halloween_roles:
                if str(role.name).startswith("Halloween Candy Collector") and str(role.name).split(" ")[3] == str(datetime.datetime.now().year):
                    self.halloween_reward_role = role

            # Creating halloween reward role if it does not exist
            if self.halloween_reward_role == None:
                self.halloween_reward_role = await self.bot.guild.create_role(name=f"Halloween Candy Collector {datetime.datetime.now().year}",color=0xe67e22)

            # Change bot avatar to halloween edition
            with open(os.path.join("data","images","bot_avatar_halloween.png"), 'rb') as image:
                image_data = image.read()
                await self.bot.user.edit(avatar=image_data)

            # Creating persistent views
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
        if self.halloween_notification_embed == None:
            embed = discord.Embed(title=self.halloween_notification_title_text, color=0xfa5c07)
            embed.add_field(name="Beschreibung:",value="Hier kannst du entscheiden, ob du Benachrichtigungen erhalten willst!")
            thumbnail = discord.File(os.path.join("data","images","halloweenbell.png"), filename='halloweenbell.png')  
            embed.set_thumbnail(url="attachment://halloweenbell.png")
            embed = await self.halloween_text_channel.send(self.halloween_looter_role.mention,file=thumbnail,embed=embed,view=self.halloween_notification_view)

    async def update(self):

        # Count down time sub events
        self.lootbag_wait_time = max(0,self.lootbag_wait_time-1)
        self.candy_steal_timer = max(0,self.candy_steal_timer-1)
        self.steal["timer"] = max(0,self.steal["timer"]-1)

        # Handling candy steal timeout
        for member in self.steal_timeout.copy():
            self.steal_timeout[member] = max(0,self.steal_timeout[member]-1)
            if self.steal_timeout[member] == 0:
                del self.steal_timeout[member]
        
        # Lootbag event
        if self.lootbag_wait_time == 0:
            await self.generate_lootbag()

            # Set new time for lootbag to appear
            self.lootbag_wait_time = random.randint(2,7)

        # Candy steal event
        if self.candy_steal_timer == 0:
            await self.steal_candy()

            # Set new time for bot to steal
            self.candy_steal_timer = random.randint(10,30)
        
        # End of steal event
        if self.steal["timer"] == 0 and self.steal["member"] != None:
            await self.bot.member_manager.check()
            for member in self.bot.member_manager.member_list:
                if member.id == self.steal["member"]:

                    # Coin penalty
                    member.coins = max(0,member.coins-5)
                    self.bot.member_manager.save(member)
                    
                    # Not mentioned announcement
                    embed = discord.Embed(title=f'🎃 {member.name} hat keine Süßigkeiten abgegeben! 🎃' , color=0xfa5c07)
                    embed.add_field(name="Beschreibung:",value=f"{member.name} hat nicht innerhalb von 5 Minuten {self.steal["candy"]} Süßigkeiten abgegeben. Dafür wurden 5 Münzen abgezogen.")
                    embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
                    await self.halloween_text_channel.send(embed=embed)

                    # Deleting messages to not use much space
                    try:
                        await self.steal["embed"].delete()
                    except Exception as e:
                        log(WARNING,f"Failed to delete steal info message: {e}")

                    # Resetting steal variable
                    self.steal = {"timer":0,"member":None,"candy":0,"embed":None}

    async def generate_lootbag(self):

        # Generate clickable loot bag embed
        embed = discord.Embed(title="Ein Lootbag ist erschienen", color=0xfa5c07)
        embed.add_field(name="Beschreibung:",value=f"Sammle {SWEETS_GOAL} Süßigkeiten um eine spezielle Rolle zu erhalten!")
        thumbnail = discord.File(os.path.join("data","images","candybag.png"), filename='candybag.png')  
        embed.set_thumbnail(url="attachment://candybag.png")
        embed = await self.halloween_text_channel.send(self.halloween_looter_role.mention,file=thumbnail,embed=embed,view=self.halloween_loot_bag_view)
        self.bot.persistent_views.clear()

    async def steal_candy(self):
        
        # Filter for possible member to steal from
        steal_list = []
        await self.bot.member_manager.check()
        for member in self.bot.member_manager.member_list:
            if member.candy >= CANDY_STEAL_THRESHOLD or member.coins >= COIN_STEAL_THRESHOLD:
                if member.id not in self.steal_timeout:
                    steal_list.append(member.id)
        
        # Check if there is a member to steal from
        if steal_list != []:
            self.steal["member"] = steal_list[random.randint(0,len(steal_list)-1)]
            self.steal["timer"] = 1
            self.steal_timeout[self.steal["member"]] = 35

            # Create steal data
            discord_member = self.bot.get_user(self.steal["member"])
            self.steal["candy"] = random.randint(5,10)

            # Steal task announcement
            embed = discord.Embed(title=f'🍬 {discord_member.name}, Süßes oder Saures! 🍬' , color=0xfa5c07)
            embed.add_field(name="Beschreibung:",value=f"{discord_member.name} du wurdest ausgewählt {self.steal["candy"]} Süßigkeiten abzugeben! Solltest du nicht in 5 Minuten reagiert haben, werden dir 5 Münzen abgezogen")
            embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
            view = discord.ui.View(timeout=None)
            view.add_item(HalloweenStealButton(self))
            self.steal["embed"] = await self.halloween_text_channel.send(discord_member.mention ,embed=embed,view=view)

    async def end(self):
        await super().end()

        # Create a summary of the collected candy
        await self.bot.member_manager.check()
        embed = discord.Embed(title=f'🍬Das Event ist vorbei, hier ist die auswertung🍬' , color=0xfa5c07)
        for member in self.bot.member_manager.member_list:
            if member.candy > 0:
                embed.add_field(name=f"{member.name}",value=f"{member.candy} 🍬", inline=False)
        embed.set_footer(text=f'[{str(datetime.datetime.today().strftime("%d.%m.%Y"))} {str(datetime.datetime.today().strftime("%H:%M"))}]')
        await self.halloween_text_channel.send(self.halloween_looter_role.mention ,embed=embed)

        # Set halloween channel to read only
        permission = discord.PermissionOverwrite()
        permission.send_messages = False
        await self.halloween_text_channel.set_permissions(self.bot.member_role, overwrite=permission)

        # Remove event role from everybody
        for member in self.bot.get_all_members():
            await member.remove_roles(self.halloween_looter_role)

        # Reset event variables
        self.lootbag_wait_time = 0
        self.candy_steal_timer = 0
        self.steal = {"timer":0,"member":None,"candy":0,"embed":None}
        self.halloween_text_channel = None
        self.halloween_chat_category = None
        self.halloween_looter_role = None
        self.halloween_reward_role = None
        self.halloween_notification_embed = None
        self.halloween_notification_view = None
        self.halloween_loot_bag_view = None
        self.prepared = False

        # Change bot avatar to normal
        with open(os.path.join("data","images","bot_avatar.png"), 'rb') as image:
            image_data = image.read()
            await self.bot.user.edit(avatar=image_data)

        # Reset game status
        activity = discord.Game(name="Frostlightgames")
        await self.bot.change_presence(activity=activity)