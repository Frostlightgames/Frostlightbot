import discord
import datetime
from main import slash,bot

@slash.command(name="stop",description="[Moderation] Stopt den Frostlightbot",guild=discord.Object(id=670321104866377748))
async def stop_command(interaction:discord.Integration):
    admin = False
    for role in interaction.user.roles:
        if role.id in [1010668967913861192]:
            admin = True
            break

    now = datetime.datetime.now()
    timestamp = now.strftime("[%d.%m.%Y %H:%M]")

    if admin:
        embed = discord.Embed(title="Bot Stop", color=0x000000)
        embed.add_field(name=f"Gestoppt von {interaction.user.name}",value=timestamp,inline=True)
        await bot.log_text_channel.send(embed=embed)

        embed = discord.Embed(title="Frostlightbot wurde gestoppt", color=0x262626)
        embed.set_footer(text=timestamp)
        await interaction.response.send_message(embed=embed)

        await bot.close()
    else:
        embed = discord.Embed(title="Keine Berechtigung für diesen Befehl", color=0x262626)
        embed.set_footer(text=timestamp)
        await interaction.response.send_message(embed=embed)