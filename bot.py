import os

from discord import Colour, Embed
from discord.ext.commands import Bot, Context

from utils import College

bot = Bot("ox!")


async def send_error(ctx: Context, title: str, message: str):
    embed = Embed(
        title=title,
        description=message,
        colour=Colour.red()
    )

    await ctx.send(embed=embed)


@bot.group("college", aliases=["clg"])
async def college_group(ctx: Context):
    pass


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

    embed = Embed(
        title=college.name,
        description=await college.get_summary(),
        colour=Colour.green()
    )

    await ctx.send(embed=embed)


bot.run(os.environ.get("BOT_TOKEN"))
