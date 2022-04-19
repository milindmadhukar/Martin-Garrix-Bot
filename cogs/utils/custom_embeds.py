import discord

async def success_embed(title, description=None):
    embed = discord.Embed(title=f"<a:tick:810462879374770186>  {title}",
                          colour=discord.Color.green())
    if description is not None:
        embed.description = description
    return embed

async def failure_embed(title, description=None):
    embed = discord.Embed(title=f"<a:cross:810462920810561556>  {title}",
                          colour=discord.Color.red())
    if description is not None:
        embed.description = description
    return embed