import random
import asyncio
import discord
import textwrap
import datetime

from zoneinfo import ZoneInfo
from main import FrostlightBot
from data.classes.logger import LOGGER
from data.classes.member import Member
from data.events.halloween.halloween import HalloweenEvent, SWEETS_GOAL, LOOT_BAG_REMAIN_TIMER

class HalloweenLootBagButton(discord.ui.Button):
    def __init__(self,bot:FrostlightBot,event:HalloweenEvent):
        self.bot = bot
        self.event = event
        self.year = datetime.datetime.now(ZoneInfo("Europe/Berlin")).year

        super().__init__(style=discord.ButtonStyle.blurple, label="Halloween Snacks",custom_id=f"HalloweenLootBagButton{datetime.datetime.now(ZoneInfo("Europe/Berlin")).year}")

    async def callback(self, interaction: discord.Interaction):

        # Event is over
        if not self.event.check_event_time_window() or self.year != datetime.datetime.now(ZoneInfo("Europe/Berlin")).year:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y • %H:%M"))
            return await interaction.response.send_message(embed=embed,ephemeral=True)
        
        # Member already collected this reward
        if interaction.user.id in self.event.halloween_loot_bag_collected_list:
            return await interaction.response.defer()
        
        # Someone pressed collect button
        try:    
            self.event.halloween_loot_bag_collected_list.append(interaction.user.id)

            # Calculate reward
            candy = random.randint(3,10)
            coins = random.randint(2,5)

            # Generating double candy after 18:00
            if datetime.datetime.now(ZoneInfo("Europe/Berlin")).hour >= 18:
                candy *= 2

            # Applying reward
            member = self.bot.member_manager.get(interaction.user.id)
            member.candy += candy
            member.coins += coins

            # Try to delete loot bag embed after 3 seconds if not already marked for deletion
            asyncio.create_task(self.delete_loot_bag_embed(interaction))

            if member.candy >= SWEETS_GOAL and member.candy-candy < SWEETS_GOAL:
                
                # Sweets goal just reached
                await self.send_reached_goal_message(interaction)
                
            elif member.candy < SWEETS_GOAL:

                # Sweets goal not yet reached
                await self.send_collection_message(interaction, candy, coins, member)
            else:

                # Sweets goal already reached
                await self.send_goal_already_reached_message(interaction, member)

        except Exception as e:
            await LOGGER.error(f"Failed to open Lootbag: {e}")

    async def send_reached_goal_message(self, interaction: discord.Interaction):

        # Sweets goal reached
        await interaction.user.add_roles(self.event.halloween_reward_role)
        embed = discord.Embed(title=f'👻🎃🦇 **{interaction.user.name} hat das Süßigkeiten Ziel erreicht!** 🦇🎃👻' , color=0xfa5c07)
        embed.set_footer(text=datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y • %H:%M"))
        await self.event.halloween_text_channel.send(embed=embed)
        await interaction.response.defer()

    async def send_collection_message(self, interaction: discord.Interaction, candy: int, coins: int, member: Member):

        # Collection information
        progress_ratio = min(member.candy / SWEETS_GOAL, 1)
        filled = int(15 * progress_ratio)
        bar = f"{'🟧' * filled}{'⬛' * (15 - filled)}"
        percent = int(progress_ratio * 100)

        embed = discord.Embed(title=f"🎃 {interaction.user.name} hat einen Lootbag geöffnet! 🎃",color=0xfa5c07)
        embed.description = textwrap.dedent(f"""
                **{interaction.user.name}** hat darin Süßigkeiten und Münzen gefunden!

                🍬 **Süßigkeiten:** `{candy}`
                <a:frostlightcoin:857720879089975326> **Münzen:** `{coins}`
                
                **Sammelstatus:** `{member.candy}/{SWEETS_GOAL}`
                `{bar}` {percent}%""")
        embed.set_thumbnail(url="attachment://candybag.png")
        embed.set_footer(text=datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y • %H:%M"))
        info_message = await self.event.halloween_text_channel.send(embed=embed)
        await interaction.response.defer()

        # Deleting messages to not use much space
        await asyncio.sleep(15)
        try:
            await info_message.delete()
        except Exception as e:
            await LOGGER.warning(f"Failed to delete collection info message: {e}")

    async def send_goal_already_reached_message(self, interaction: discord.Interaction, member: Member):

        # Sweets goal already reached
        embed = discord.Embed(title=f"Du hast bereits {member.candy} Süßigkeiten gesammelt, aber hör nicht auf mit sammeln! 🍬" , color=0xfa5c07)
        embed.set_footer(text=datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y • %H:%M"))
        await interaction.response.send_message(embed=embed,ephemeral=True)

    async def delete_loot_bag_embed(self, interaction: discord.Interaction):

        # Delete marked loot bag embed
        try:
            if not self.event.halloween_loot_bag_marked_for_deletion:
                self.event.halloween_loot_bag_marked_for_deletion = True
                try:
                    await asyncio.sleep(LOOT_BAG_REMAIN_TIMER)
                    await interaction.message.delete()
                except Exception as e:
                    await LOGGER.warning(f"Failed to delete collection info message: {e}")
                self.event.halloween_loot_bag_collected_list = []
                self.event.halloween_loot_bag_marked_for_deletion = False
                self.event.halloween_last_loot_bag_message = None
        except Exception as e:
            await LOGGER.error(f"Could not delete loot bag embed | {e}")