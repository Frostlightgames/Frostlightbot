import os
import random
import discord
import asyncio
import datetime

from data.events.halloween.halloween import HalloweenEvent

async def generate_slot_machine(event: HalloweenEvent):

    # Generate clickable slot machine embed
    HINT_TEXTS = [
        (0, "Ein kalter Wind weht durch das Gruselcasino... 🍂 Vielleicht ist heute nicht dein Tag."),
        (1, "Die Schatten flüstern... 'Nicht jede Münze glänzt im Dunkeln.' 👻"),
        (2, "Ein Rabe kräht dreimal vor deinem Einsatz. 🪶 Ein schlechtes Omen?"),
        (3, "Die Kürbisse kichern leise... vielleicht bringen sie Glück, vielleicht nur Spuk. 🎃"),
        (4, "Ein leises Klingen erklingt in der Ferne oder war es nur der Wind? 🔔"),
        (5, "Dein Einsatz liegt auf dem Tisch. Die Geister tuscheln... aber niemand versteht ihre Sprache. 🕯️"),
        (6, "Das Rad der Nacht dreht sich. Ob's dir wohlgesinnt ist? 🌒"),
        (7, "Eine schwarze Katze schaut dich an ruhig, unbeteiligt. 🐈‍⬛"),
        (8, "Ein Tropfen Wachs fällt von der Kerze... formt fast ein Herz, fast ein Schädel. 🕯️💀"),
        (9, "Ein goldenes Licht flackert kurz auf und alles riecht nach Karamell und Glück. 🍭✨"),
    ]

    # Choosing slot machine type
    state, hint_text = random.choice(HINT_TEXTS)
    event.halloween_slot_machine_view.state = state

    # Sending slot machine
    embed = discord.Embed(title="🎰 Das Spukrad der Süßigkeiten erwacht! 🎰",color=0xfa5c07)
    embed.description = f"Das Spukrad verschwindet <t:{int((datetime.datetime.now()+datetime.timedelta(minutes=1)).timestamp())}:R>"
    embed.add_field(name="Beschreibung",value=hint_text)
    embed.set_footer(text=datetime.datetime.now().strftime("%d.%m.%Y • %H:%M"))
    embed.set_thumbnail(url="attachment://slotmachine.png")
    thumbnail = discord.File(os.path.join("data", "images", "slotmachine.png"), filename="slotmachine.png")
    embed = await event.halloween_text_channel.send(event.halloween_looter_role.mention,file=thumbnail,embed=embed,view=event.halloween_slot_machine_view)
    event.halloween_last_slot_machine_message = embed.id
    event.bot.persistent_views.clear()

    # After 60 seconds delete slot machine message
    asyncio.create_task(delete_slot_machine(embed,event))

async def delete_slot_machine(embed:discord.Embed,event:HalloweenEvent):

    # Delete slot machine after 60 seconds for a new to spawn
    await asyncio.sleep(60)
    await embed.delete()
    event.halloween_last_slot_machine_message = None
    event.halloween_slot_machine_collected_list = []