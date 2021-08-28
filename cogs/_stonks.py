import discord
from discord.ext import commands
from discord.embeds import Embed
from discord import Colour
from aiohttp import request

# from discord.ext import menus

url = "https://thestonksapi.herokuapp.com/"

buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9", u"\u23F9"]

# class NewsMenu(menus.Menu):
#     def __init__(self, msg, embeds):
#         self.embeds = embeds
#         self.count = 0
#         super().__init__(timeout=180.0, delete_message_after=True)
#
#     async def send_initial_message(self, ctx, channel):
#         await channel.send(embed = self.embeds[self.count])
#
#     @menus.button(buttons[0])
#     async def first_em(self, payload):
#         self.count = 0
#         await self.message.edit(embed = self.embeds[self.count])
#
#     @menus.button(buttons[1])
#     async def previous_em(self, payload):
#         if self.count > 0 : self.count -= 1
#         await self.message.edit(embed = self.embeds[self.count])
#
#     @menus.button(buttons[2])
#     async def next_em(self, payload):
#         if self.count < len(self.embeds) - 1 : self.count += 1
#         await self.message.edit(embed = self.embeds[self.count])
#
#     @menus.button(buttons[3])
#     async def last_em(self, payload):
#         self.count = len(self.embeds) - 1
#         await self.message.edit(embed = self.embeds[self.count])
#
#     @menus.button(buttons[4])
#     async def stop_em(self, payload):
#         self.stop()
#         await self.message.delete(delay=10)

class Stocks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stock(self, ctx, stock, index):
        data = {}
        async with request('GET', f'{url}stocks/{stock}:{index}' ) as resp:
            try:
                data = await resp.json()
            except:
                return await ctx.send("No data found.")
        if data['change'] < 0:
            color=Colour.red()
            emote='🔴'
        elif data['change'] >= 0:
            color=Colour.green()
            emote='🟢'
        em = Embed(title=str(data['stock_name']), color=color)
        em.add_field(name='Current Value: ', value=str(data['price']) + '   ' + emote+ '  ({}%)'.format(data['changepercent']), inline=False)
        em.add_field(name='Previous Close: ', value=str(data['previous_close']), inline=False)
        if data['day_range']:
            em.add_field(name='Day Range: ', value=data['day_range'], inline=False)
        if data['year_range']:
            em.add_field(name='Year Range: ', value=data['year_range'], inline=False)
        if data['market_cap']:
            em.add_field(name='Market Cap: ', value=data['market_cap'], inline=False)
        if data['primary_exchange']:
            em.add_field(name='Primary Exchange: ', value=data['primary_exchange'], inline=False)
        await ctx.send(embed=em)
        
    # @commands.command()
    # async def news(self, ctx, stock, index):
    #     data = {}
    #     async with request('GET', f'{url}stocks/news/{stock}:{index}' ) as resp:
    #         try:
    #             data = await resp.json()
    #         except Exception as e:
    #             print(e)
    #             return await ctx.send("No data found.")
    #         embeds = []
    #         for i in data:
    #             embed = discord.Embed(description=f"[{i['title']}]({i['article_link']})", colour=discord.Color.orange())
    #             embed.set_thumbnail(url=i['thumbnail_link'])
    #             embed.set_footer(text=f"Article from {i['source']}")
    #             embeds.append(embed)
    #
    #     m = NewsMenu(ctx.message,embeds)
    #     await m.start(ctx)

    @commands.command()
    async def crypto(self, ctx, crypto_name, currency):
        data = {}
        async with request('GET', f'{url}crypto/{crypto_name}:{currency}' ) as resp:
            try:
                data = await resp.json()
            except Exception as e:
                print(e)
                return await ctx.send("No data found.")
        if data['change'] < 0:
            color=Colour.red()
            emote='🔴'
        elif data['change'] >= 0:
            color=Colour.green()
            emote='🟢'
        em = Embed(title=str(data['crypto_name']), description= data['description'] ,color=color)
        em.add_field(name='Current Value: ', value=str(data['price']) + '   ' + emote+ '  ({}%)'.format(data['change_percent']), inline=False)
        em.add_field(name='Previous Close: ', value=str(data['previous_close']), inline=False)
        
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Stocks(bot))