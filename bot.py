import os
import random

from discord import Colour, Embed
from discord.ext.commands import Bot, Context

from utils import College, get_current_ip

bot = Bot(("ox!", "Ox!", "OX!", "oX!"), case_insensitive=True)


async def send_error(ctx: Context, title: str, message: str):
    embed = Embed(
        title=title,
        description=message,
        colour=Colour.red()
    )

    await ctx.send(embed=embed)


@bot.group("college", aliases=["clg"], invoke_without_command=True)
async def college_group(ctx: Context, *, college_name: str = ""):
    await college_info(ctx, college_name=college_name)


@college_group.command("info", aliases=["summary"])
async def college_info(ctx: Context, *, college_name: str = ""):
    if not college_name:
        await send_error(ctx, "Invalid command.", "Please supply a college name.")
        return

    matches = College.search_for_college(college_name, match_threshold=0.62)

    if not matches:
        await send_error(ctx, "Unknown college.", "Your search didn't match any colleges.")
        return

    elif len(matches) > 1:
        match_list = "\n".join(f"- {college}" for college in matches)
        message = (
            "Your search equally matches the following colleges:\n\n"
            f"{match_list}\n\n"
            "Please use a more specific query."
        )

        await send_error(ctx, "Ambiguous query.", message)
        return

    # the remaining set will only contain one item.
    college, = matches
    students = await college.get_students()
    founded = await college.get_founded()
    admissions = await college.get_admissions_contacts()

    embed = Embed(
        title=college.name,
        description=await college.get_summary(),
        colour=Colour.green()
    )

    embed.add_field(name="Students", value=students)
    embed.add_field(name="Founded", value=founded)
    embed.add_field(name="Contact Admissions", value=admissions)
    embed.add_field(
        name="\u200b",
        value=f"[Read more...]({college.info_page})",
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command()
async def terraria(ctx: Context):
    ip_string = await get_current_ip()

    embed = Embed(
        color=random.choice([0x55cc55, 0x773399, 0x993333, 0x66eeff]),
        title="Terraria Server!",
        description=(
            "The IP address for our spicy fun __master mode__ server changes quite "
            "frequently. Simply run this command when you need the current IP address! :)"
        )
    )

    current_info = (
        f"IP: {ip_string}\n"
        "Port: 2021\n"
        "Password: pogchamp"
    )

    embed.add_field(name="Join us!", value=current_info)
    embed.set_footer(text="If it's your first time joining us, please start with a new character!")
    await ctx.reply(embed=embed)


@bot.command(aliases=["mc"])
async def minecraft(ctx: Context):
    embed = Embed(
        color=0x55cc55,
        title="Minecraft Server!",
        description=(
            "Want to play with some fellow Oxford applicants? Come join our casual "
            "vanilla Minecraft server for version 1.16.5! :)"
        )
    )

    embed.add_field(name="Join us!", value="IP Address: 51.83.233.138:25590 **or** oxfordoh.ramshard.net")
    await ctx.reply(embed=embed)


bot.run(os.environ.get("BOT_TOKEN"))
