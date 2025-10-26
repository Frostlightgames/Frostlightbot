import os
import discord
import datetime

from data.events.halloween.halloween import SWEETS_GOAL, HalloweenEvent

async def generate_loot_bag(event: HalloweenEvent):

    # Generate clickable loot bag embed
    embed = discord.Embed(title="🎃 Ein geheimnisvoller Lootbag ist erschienen! 🎃",color=0xfa5c07)
    embed.add_field(name="Beschreibung:", value=f"Sammle **{SWEETS_GOAL} Süßigkeiten** 🍬, um eine **besondere Rolle** zu erhalten!")
    embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
    embed.set_thumbnail(url="attachment://candybag.png")
    thumbnail = discord.File(os.path.join("data", "images", "candybag.png"), filename="candybag.png")
    embed = await event.halloween_text_channel.send(event.halloween_looter_role.mention,file=thumbnail,embed=embed,view=event.halloween_loot_bag_view)
    event.halloween_last_loot_bag_message = embed.id
    event.bot.persistent_views.clear()