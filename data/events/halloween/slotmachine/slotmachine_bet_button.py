import random
import asyncio
import discord
import textwrap
import datetime

from main import FrostlightBot
from data.classes.member import Member
from data.classes.logger import LOGGER
from data.classes.database import DATABASE
from data.events.halloween.halloween import HalloweenEvent, SWEETS_GOAL

STATE_PROBABILITIES = {
    # Lose None Win
    0: [80, 15, 5],
    1: [80, 15, 5],
    2: [50, 30, 20],
    3: [50, 30, 20],
    4: [30, 40, 30],
    5: [30, 40, 30],
    6: [20, 35, 45],
    7: [20, 35, 45],
    8: [10, 40, 50],
    9: [0, 5, 95],
}

BET_MODIFIER = {
    1: 0.75,
    10: 1.0,
    25: 1.3,
}

class HalloweenSlotMachineSelect(discord.ui.Select):
    def __init__(self,bot:FrostlightBot,event:HalloweenEvent):
        self.bot = bot
        self.event = event
        self.year = datetime.datetime.now().year

        super().__init__(placeholder="Wähle deinen Einsatz... 🎰",min_values=1,max_values=1,custom_id=f"HalloweenSlotMachine{datetime.datetime.now().year}",
            options = [
                discord.SelectOption(label="(1) Ein Bonbon", description="Ein kleiner Biss ins Unbekannte...", emoji="🍬"),
                discord.SelectOption(label="(10) Eine Hand voll Süßigkeiten", description="Mutig ... das Spukrad dreht sich...", emoji="🍫"),
                discord.SelectOption(label="(25) Ein Süßigkeitenkorb", description="Große Einsätze ... großes Risiko.", emoji="🍿")
            ]
        )

    async def calculate_slot_result(self, state: int, bet: int):
        weights = STATE_PROBABILITIES[state].copy()
        modifier = BET_MODIFIER.get(bet, 1.0)

        # Adjust weights: riskier bets tilt toward losing
        weights[0] = int(weights[0] * modifier)          # lose
        weights[2] = max(1, int(weights[2] / modifier))  # win

        outcome = random.choices(["lose", "stay", "win"],weights=weights,k=1)[0]
        return outcome
        
    async def callback(self, interaction: discord.Interaction):

        # Event is over
        if not self.event.check_event_time_window() or self.year != datetime.datetime.now().year:
            embed = discord.Embed(title=f"Das Event für dieses Jahr ist bereits vorbei" , color=0xfa5c07)
            embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
            return await interaction.response.send_message(embed=embed,ephemeral=True)
        
        # Member already played at this slot machine
        if interaction.user.id in self.event.halloween_slot_machine_collected_list:
            return await self.send_already_played_message(interaction)
        
        # Someone chooses a bet
        try:
            selection = self.values[0]
            state = getattr(self.view, "state", 5)
            member = self.bot.member_manager.get(interaction.user.id)

            member_free_spins = int(DATABASE.get_config(f"halloween_free_spins_{member.name}","0"))
            free_spin = False

            # Getting bet from embed
            if "25" in selection:
                bet = 25
            elif "10" in selection:
                bet = 10
            else:
                bet = 1

            # Not enough candy to play
            if member.candy < bet and member_free_spins == 0:
                return await self.send_not_enough_sweets_message(interaction, member)
            
            # Free spins
            if member_free_spins > 0:
                member_free_spins -= 1
                free_spin = True
                DATABASE.set_config(f"halloween_free_spins_{member.name}",str(member_free_spins))
                    
            self.event.halloween_slot_machine_collected_list.append(interaction.user.id)
            
            # Calculate result
            result = await self.calculate_slot_result(state, bet)

            # Loosing bet candy
            if result == "lose":

                # Making sure to not loose to much
                if not free_spin:
                    if member.candy >= 100:
                        member.candy = max(100,member.candy - bet)
                    else:
                        member.candy = max(0,member.candy - bet)

                await self.send_loose_message(interaction, bet, member)
            
            # Keeping candy
            elif result == "stay":
                await self.send_stay_message(interaction, bet, member)

            # Winning the bet candy
            else:
                member.candy += bet

                if member.candy >= SWEETS_GOAL and member.candy-bet < SWEETS_GOAL:
                
                    # Sweets goal just reached
                    await self.send_reached_goal_message(interaction, bet, member)
                    
                elif member.candy < SWEETS_GOAL:

                    # Sweets goal not yet reached
                    await self.send_collection_message(interaction, bet, member)
                else:

                    # Sweets goal already reached
                    await self.send_goal_already_reached_message(interaction, bet, member)
            
        except Exception as e:
            await LOGGER.error(f"Failed to bet on slot machine: {e}")

    async def send_already_played_message(self, interaction: discord.Interaction):

        # Already played
        await interaction.user.add_roles(self.event.halloween_reward_role)
        embed = discord.Embed(title=f"🚫 Du hast hast bereits an diesem Spukrad gespielt! Warte bis das nächste kommt." , color=0xfa5c07)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def send_not_enough_sweets_message(self, interaction: discord.Interaction, member: Member):

        # Not enough sweets
        await interaction.user.add_roles(self.event.halloween_reward_role)
        embed = discord.Embed(title=f"🚫 Du hast nur {member.candy} Süßigkeiten, **nicht genug** für diesen Einsatz!" , color=0xfa5c07)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def send_reached_goal_message(self, interaction: discord.Interaction, bet: int, member: Member):

        # Sweets goal reached
        await interaction.user.add_roles(self.event.halloween_reward_role)
        embed = discord.Embed(title=f"🎉👻 {interaction.user.name} hat das Süßigkeiten-Ziel erreicht! 🍬🏆",color=0xfa5c07)
        embed.description = textwrap.dedent(f"Deine **{bet}** eingesetzten Süßigkeiten haben dich direkt ans Ziel gebracht! 🎃✨")
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        await self.event.halloween_text_channel.send(embed=embed)
        await interaction.response.defer()

    async def send_collection_message(self, interaction: discord.Interaction, bet: int, member: Member):

        # Player won
        progress_ratio = min(member.candy / SWEETS_GOAL, 1)
        filled = int(15 * progress_ratio)
        bar = f"{'🟧' * filled}{'⬛' * (15 - filled)}"
        percent = int(progress_ratio * 100)

        embed = discord.Embed(title=f"🧙‍♂️ {interaction.user.name} hat das Spukrad gedreht... und gewonnen! 🎉",color=0xfa5c07)
        embed.description = textwrap.dedent(f"""
            Deine **{bet}** eingesetzten Süßigkeiten 🍬 haben sich verdoppelt! 👻

            **Aktueller Süßigkeitenstand:** `{member.candy}`  
            `{bar}` {percent}%
        """)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        message = await self.event.halloween_text_channel.send(embed=embed)
        await interaction.response.defer()
        await self.delete_info_message(message)

    async def send_goal_already_reached_message(self, interaction: discord.Interaction, bet: int, member: Member):

        # Player already reached the goal
        embed = discord.Embed(title=f"🍬 {interaction.user.name} sammelt mit einem vollen Süßigkeiten Korb weiterweiter! 🎃",color=0xfa5c07)
        embed.description = textwrap.dedent(f"""
            {interaction.user.name}, hat das Süßigkeiten-Ziel bereits erreicht 👻.

            Dein Einsatz von **{bet}** Süßigkeiten zahlt sich weiter aus.  
            **Aktueller Süßigkeitenstand:** `{member.candy}/{SWEETS_GOAL}`  
        """)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        message = await self.event.halloween_text_channel.send(embed=embed)
        await interaction.response.defer()
        await self.delete_info_message(message)

    async def send_stay_message(self, interaction: discord.Interaction, bet:int, member: Member):

        # Player does not win or lose
        progress_ratio = min(member.candy / SWEETS_GOAL, 1)
        filled = int(15 * progress_ratio)
        bar = f"{'🟧' * filled}{'⬛' * (15 - filled)}"
        percent = int(progress_ratio * 100)

        embed = discord.Embed(title=f"🕯️ {interaction.user.name} dreht das Spukrad... nichts passiert.",color=0xfa5c07)
        embed.description = textwrap.dedent(f"""
            Deine **{bet}** gesetzten Süßigkeiten 🍬 bleiben unberührt 🕸️.  

            **Aktueller Süßigkeitenstand:** `{member.candy}`  
            `{bar}` {percent}%
        """)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        message = await self.event.halloween_text_channel.send(embed=embed)
        await interaction.response.defer()
        await self.delete_info_message(message)

    async def send_loose_message(self, interaction: discord.Interaction, bet:int, member: Member):

        # Player looses bet 
        progress_ratio = min(member.candy / SWEETS_GOAL, 1)
        filled = int(15 * progress_ratio)
        bar = f"{'🟧' * filled}{'⬛' * (15 - filled)}"
        percent = int(progress_ratio * 100)

        embed = discord.Embed(title=f"💀 {interaction.user.name} wurde vom Spukrad verflucht!",color=0xfa5c07)
        embed.description = textwrap.dedent(f"""
            Deine **{bet}** gesetzten Süßigkeiten 🍬 verschwinden in den Schatten. 👻

            **Aktueller Süßigkeitenstand:** `{member.candy}`  
            `{bar}` {percent}%
        """)
        embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
        message = await self.event.halloween_text_channel.send(embed=embed)
        await interaction.response.defer()
        await self.delete_info_message(message)

    async def delete_info_message(self,message):

        # Deleting messages to not use much space
        await asyncio.sleep(15)
        try:
            await message.delete()
        except Exception as e:
            await LOGGER.warning(f"Failed to delete collection info message: {e}")