from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont
from itertools import cycle
from .DataBase.user import User

templates = cycle(["red", "green", "pink", "yellow"])

def humanize(xp):
    if xp < 1000:
        return xp
    else:
        xp = xp/1000
        xp = str(xp).split('.')
        xp_float = xp[1][0:2]

        return f'{xp[0]}.{xp_float}K'

def f_xp_for_next_level(lvl):
    return 5*lvl**2 + 50*lvl + 100


def get_total_xp(lvl):
    sum = 0
    for i in range(lvl):
        sum += f_xp_for_next_level(i)

    return sum

def get_user_level_data(total_xp: int):
    sum = 0
    lvl = 0
    while sum <= total_xp:
        sum += f_xp_for_next_level(lvl)
        lvl += 1
    lvl -= 1
    return {'lvl': lvl, 'xp_for_next_lvl' : f_xp_for_next_level(lvl), 'current_xp' : total_xp - get_total_xp(lvl) }

def rank_picture(user: User, member_name, rank, img_data):

    lvl_data = get_user_level_data(user.total_xp)

    percentage = lvl_data['current_xp']/lvl_data['xp_for_next_lvl']

    bg = Image.open("./assets/grey_bg.png")

    colour = next(templates)

    WIDTH = 680
    progress = Image.new('RGBA', (int(WIDTH*percentage), 50), colour)
    bg.paste(progress, (261,194))

    template = Image.open(f"./assets/{colour}.png")

    pfp = Image.open(img_data).convert('RGB')
    pfp = pfp.resize((173,173))


    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    pfp.putalpha(mask)


    pfp = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
    pfp.putalpha(mask)

    template.paste(pfp, (43,63), mask=pfp)

    bg.paste(template,(0,0), mask=template)

    draw = ImageDraw.Draw(bg)

    txt = member_name

    if len(txt) <= 20:
        fontsize = 36
        font = ImageFont.truetype("./assets/font.ttf", fontsize)

    else:
        fontsize = 12
        img_fraction = 0.6

        font = ImageFont.truetype("./assets/font.ttf", fontsize)
        while font.getsize(txt)[0] < img_fraction*WIDTH :
            fontsize += 1
            font = ImageFont.truetype("./assets/font.ttf", fontsize)

        fontsize -= 1
        font = ImageFont.truetype("./assets/font.ttf", fontsize)


    draw.text((284,145),txt, (255,255,255), font=font)

    current_xp = humanize(lvl_data['current_xp'])
    xp_for_next_level = humanize(lvl_data['xp_for_next_lvl'])

    txt = f"{current_xp}/{xp_for_next_level}"
    fontsize = 32
    font = ImageFont.truetype("./assets/font.ttf", fontsize)
    draw.text(((925-font.getsize(txt)[0]),150),txt, (255,255,255), font=font)

    txt = "LEVEL"
    fontsize = 22
    font = ImageFont.truetype("./assets/font.ttf", fontsize)
    lvl_x = (845-font.getsize(txt)[0])
    draw.text((lvl_x,77),txt, (255,255,255), font=font)

    txt = str(lvl_data['lvl'])
    fontsize = 50
    font = ImageFont.truetype("./assets/font.ttf", fontsize)
    draw.text((855,50),txt, (255,255,255), font=font)

    txt = f'#{str(rank)}'
    fontsize = 50
    rank_font = ImageFont.truetype("./assets/font.ttf", fontsize)
    rank_size = font.getsize(txt)[0]
    draw.text((lvl_x-rank_size-30,50),txt, (255,255,255), font=rank_font)

    txt= "RANK"
    fontsize = 22
    font = ImageFont.truetype("./assets/font.ttf", fontsize)
    draw.text(((lvl_x-font.getsize(txt)[0]-rank_size-37),77),txt, (255,255,255), font=font)

    image = BytesIO()
    bg.save(image, format="png")
    image.seek(0)

    return image
