from io import BytesIO
from itertools import cycle

import discord
from PIL import ImageFont, Image, ImageDraw, ImageOps

from utils.database.user import User

__all = (
    "success_embed",
    "failure_embed",
    "parse_amount",
    "rank_picture",
    "get_user_level"
    "get_user_level_data",
    "f_xp_for_next_level",
)

templates = cycle(["red", "green", "pink", "yellow"])

async def success_embed(title: str, description: str = None) -> discord.Embed:
    """
    |coro|
    This function constructs a :class:`discord.Embed` object with a success emoji and the embed colour is
    green.

    Parameters:
        title (str): This parameter takes the title that you want embed's title to be.
        description (str): This parameter takes the description you want to set in your embed's description field.
                           This parameter is optional.

    Returns:
        (discord.Embed): The constructed embed object.
    """
    embed = discord.Embed(
        title=f"<a:tick:810462879374770186>  {title}",
        colour=discord.Colour.green(),
    )
    if description is not None:
        embed.description = description

    return embed


async def failure_embed(title: str, description: str = None) -> discord.Embed:
    """
    This function constructs a :class:`discord.Embed` object with a failure emoji and the embed colour is
    red.

    Parameters:
        title (str): This parameter takes the title that you want embed's title to be.
        description (str): This parameter takes the description you want to set in your embed's description field.
                           This parameter is optional.

    Returns:
        (discord.Embed): The constructed embed object.
    """
    embed = discord.Embed(
        title=f"<a:cross:810462920810561556>  {title}",
        colour=discord.Colour.red(),
    )

    if description is not None:
        embed.description = description
    return embed

def parse_amount(amount: str, other_quantity: int) ->  int:
    """
    This function parses an amount based the parameter amount and other quantity, if the amount is a numerical character
    but its datatype is a number, it will return that number in an integer, however, if the parameter amount is 'all'
    it will return whatever value of passed in other_quantity, and if the amount is 'half', the other_quantity parameter
    is rounded by 2.
    """
    if amount.isnumeric():
        return int(amount)
    elif amount in ["full", "all", "complete", "everything"]:
        return other_quantity
    elif amount == "half":
        return other_quantity // 2
    else:
        return -1


def humanize(xp: int):
    """
    This function returns a human-readable string of a number.

    Parameters:
        xp (int): This parameter takes an integer that needs to be converted into a human-readable string.
    """
    if not isinstance(xp, int):
        raise TypeError(f"Parameter 'xp' required an integer ( int ) not {type(xp)}")
    if xp < 1000:
        return xp
    else:
        xp = xp / 1000
        xp = str(xp).split(".")
        xp_float = xp[1][0:2]

        return f"{xp[0]}.{xp_float}K"


def f_xp_for_next_level(lvl: int) -> int:
    return 5 * lvl**2 + 50 * lvl + 100


def get_total_xp(lvl: int) -> int:
    """
    This function returns the total xp that is required based on your level.

    Parameters:
        lvl (int): This parameter takes the level to base the xp requirements on.

    Returns:
        (int): The required xp.
    """
    if not isinstance(lvl, int):
        raise TypeError(f"Parameter 'lvl' required an integer ( int ) not {type(lvl)}")
    total_sum = 0
    for i in range(lvl):
        total_sum += f_xp_for_next_level(i)

    return total_sum

def get_user_level(total_xp: int) -> int:
    lvl = 0
    total_sum = 0
    while total_sum <= total_xp:
        total_sum += f_xp_for_next_level(lvl)
        lvl += 1

    return lvl - 1


def get_user_level_data(total_xp: int):
    if not isinstance(total_xp, int):
        raise TypeError(
            f"Parameter 'total_xp' required an integer ( int ) not {type(total_xp)}"
        )
    lvl = get_user_level(total_xp)
    return {
        "lvl": lvl,
        "xp_for_next_lvl": f_xp_for_next_level(lvl),
        "current_xp": total_xp - get_total_xp(lvl),
    }


def rank_picture(user: User, member_name: str, rank: int, img_data: BytesIO) -> BytesIO:
    """
    This function takes a user object, calculates its xp and levels and then returns an image which is a rank card
    that shows details about the user's achievement in pretty looking image.
    """
    lvl_data = get_user_level_data(user.total_xp)
    percentage = lvl_data["current_xp"] / lvl_data["xp_for_next_lvl"]
    bg = Image.open("./static/assets/grey_bg.png")


    colour = next(templates)
    WIDTH = 680
    progress = Image.new("RGBA", (int(WIDTH * percentage), 50), colour)
    bg.paste(progress, (261, 194))
    template = Image.open(f"./static/assets/{colour}.png")
    pfp = Image.open(img_data).convert("RGB")
    pfp = pfp.resize((173, 173))
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.Resampling.LANCZOS)
    pfp.putalpha(mask)
    pfp = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
    pfp.putalpha(mask)
    template.paste(pfp, (43, 63), mask=pfp)
    bg.paste(template, (0, 0), mask=template)
    draw = ImageDraw.Draw(bg)
    txt = member_name

    if len(txt) <= 20:
        fontsize = 36
        font = ImageFont.truetype("./static/assets/font.ttf", fontsize)

    else:
        fontsize = 12
        img_fraction = 0.6

        font = ImageFont.truetype("./static/assets/font.ttf", fontsize)
        while font.getsize(txt)[0] < img_fraction * WIDTH:
            fontsize += 1
            font = ImageFont.truetype("./static/assets/font.ttf", fontsize)

        fontsize -= 1
        font = ImageFont.truetype("./static/assets/font.ttf", fontsize)

    draw.text((284, 145), txt, (255, 255, 255), font=font)

    current_xp = humanize(lvl_data["current_xp"])
    xp_for_next_level = humanize(lvl_data["xp_for_next_lvl"])

    txt = f"{current_xp}/{xp_for_next_level}"
    fontsize = 32
    font = ImageFont.truetype("./static/assets/font.ttf", fontsize)
    draw.text(((925 - font.getsize(txt)[0]), 150), txt, (255, 255, 255), font=font)

    txt = "LEVEL"
    fontsize = 22
    font = ImageFont.truetype("./static/assets/font.ttf", fontsize)
    lvl_x = 845 - font.getsize(txt)[0]
    draw.text((lvl_x, 77), txt, (255, 255, 255), font=font)

    txt = str(lvl_data["lvl"])
    fontsize = 50
    font = ImageFont.truetype("./static/assets/font.ttf", fontsize)
    draw.text((855, 50), txt, (255, 255, 255), font=font)

    txt = f"#{str(rank)}"
    fontsize = 50
    rank_font = ImageFont.truetype("./static/assets/font.ttf", fontsize)
    rank_size = font.getsize(txt)[0]
    draw.text((lvl_x - rank_size - 30, 50), txt, (255, 255, 255), font=rank_font)

    txt = "RANK"
    fontsize = 22
    font = ImageFont.truetype("./static/assets/font.ttf", fontsize)
    draw.text(
        ((lvl_x - font.getsize(txt)[0] - rank_size - 37), 77),
        txt,
        (255, 255, 255),
        font=font,
    )

    image = BytesIO()
    bg.save(image, format="png")
    image.seek(0)

    return image
