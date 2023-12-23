from discord.ext import commands
import discord
import asyncio

from utils.database.tag import Tag

from utils.checks import is_admin, is_milind, is_staff, is_true_garrixer_check


class TagCommands(commands.Cog, name="Tags"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: commands.Context, *, name: lambda inp: inp.lower()):
        """
        Main tag group.
        """

        tag = await self.bot.database.get_tag(name=name)
        if tag is None:
            await ctx.message.delete(delay=10.0)
            message = await ctx.send("Could not find a tag with that name.")
            return await message.delete(delay=10.0)
        await ctx.send(tag.content)
        await self.bot.database.execute(
            "UPDATE tags SET uses = uses + 1 WHERE name = $1", name
        )
        return

    @tag.command()
    async def info(self, ctx: commands.Context, *, name: lambda inp: inp.lower()):
        """
        Get information regarding the specified tag.
        """
        tag = await self.bot.database.get_tag(name=name)

        if tag is None:
            await ctx.message.delete(delay=10.0)
            message = await ctx.send("Could not find a tag with that name.")
            return await message.delete(delay=10.0)

        author = self.bot.get_user(tag.creator_id)
        author = (
            str(author)
            if isinstance(author, discord.User)
            else f"(ID: {tag.creator_id})"
        )
        # TODO: Change to a nice embed
        text = (
            "Tag: {name}\n\n```prolog\nCreator: {author}\n   Uses: {uses}\n```".format(
                name=name, author=author, uses=tag.uses
            )
        )
        await ctx.send(text)
        return

    @tag.command()
    @is_true_garrixer_check()
    async def create(
        self, ctx: commands.Context, name: lambda inp: inp.lower(), *, content: str
    ):
        """
        Create a new tag.
        """
        # TODO: Allow true garrixers to create tags
        name = await commands.clean_content().convert(ctx=ctx, argument=name)
        content = await commands.clean_content().convert(ctx=ctx, argument=content)

        tag = await self.bot.database.get_tag(name=name)
        if tag is not None:
            return await ctx.send("A tag with that name already exists.")

        tag = Tag(bot=self.bot, creator_id=ctx.author.id, name=name, content=content)
        await tag.post()
        await ctx.send("You have successfully created your tag.")

    @tag.command()
    async def list(
        self, ctx: commands.Context, member: commands.MemberConverter = None
    ):
        """
        List your existing tags.
        """
        member = member or ctx.author
        query = """SELECT name FROM tags WHERE creator_id = $1 ORDER BY name, uses"""
        records = await self.bot.database.fetch(query, member.id)
        if not records:
            return await ctx.send("No tags found.")

        await ctx.send(
            f"**{len(records)} tags by {'you' if member == ctx.author else str(member)} found on this server.**"
        )

        pager = commands.Paginator()

        for record in records:
            pager.add_line(line=record["name"])

        for page in pager.pages:
            await ctx.send(page)

    @tag.command()
    @commands.cooldown(1, 3600 * 24, commands.BucketType.user)
    async def all(self, ctx: commands.Context):
        """
        List all existing tags alphabetically ordered and sends them in DMs.
        """
        records = await self.bot.database.fetch("SELECT name FROM tags ORDER BY name")

        if not records:
            return await ctx.send("This server doesn't have any tags.")

        try:
            await ctx.author.send(f"***{len(records)} tags found on this server.***")
        except discord.Forbidden:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "Could not DM you. Please open DMs for this server and run the command again",
                delete_after=20,
            )

        pager = commands.Paginator()

        for record in records:
            pager.add_line(line=record["name"])

        for page in pager.pages:
            await asyncio.sleep(1)
            await ctx.author.send(page)

        await ctx.send("Tags sent in DMs.")

    @tag.command()
    @is_true_garrixer_check()
    async def edit(
        self, ctx: commands.Context, name: lambda inp: inp.lower(), *, content: str
    ):
        """
        Edit a tag.
        """
        content = await commands.clean_content().convert(ctx=ctx, argument=content)
        member = ctx.author
        tag = await self.bot.database.get_tag(name=name)

        if tag is None:
            await ctx.message.delete(delay=10.0)
            message = await ctx.send("Could not find a tag with that name.")
            return await message.delete(delay=10.0)

        if tag.creator_id != ctx.author.id:
            if (not is_admin(member)) or (not is_milind(member)):
                return await ctx.send("You don't have permission to do that.")

        await tag.update(content=content)
        await ctx.send("You have successfully edited your tag.")
        return

    @tag.command()
    @is_true_garrixer_check()
    async def delete(self, ctx: commands.Context, *, name: lambda inp: inp.lower()):
        """
        Delete an existing tag.
        """
        tag = await self.bot.database.get_tag(name=name)
        member = ctx.author

        if tag is None:
            await ctx.message.delete(delay=10.0)
            message = await ctx.send("Could not find a tag with that name.")
            return await message.delete(delay=10.0)

        if tag.creator_id != ctx.author.id:
            if (not is_staff(member)) or (not is_milind(member)):
                return await ctx.send("You don't have permission to do that.")

        await tag.delete()
        await ctx.send("You have successfully deleted your tag.")
        return

    @tag.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def search(self, ctx: commands.Context, *, term: str):
        """
        Search for a tag given a search term.
        """
        # Test this.
        query = """SELECT name FROM tags WHERE name LIKE $1 LIMIT 10"""
        records = await self.bot.database.fetch(query, term)

        if not records:
            return await ctx.send(
                "No tags found that has the term in it's name", delete_after=10
            )
        count = "Maximum of 10" if len(records) == 10 else len(records)
        records = "\n".join([record["name"] for record in records])

        await ctx.send(
            f"**{count} tags found with search term on this server.**```\n{records}\n```"
        )
        return

    @tag.command()
    @is_true_garrixer_check()
    async def rename(
        self,
        ctx: commands.Context,
        name: lambda inp: inp.lower(),
        *,
        new_name: lambda inp: inp.lower(),
    ):
        """
        Rename a tag.
        """

        new_name = await commands.clean_content().convert(ctx=ctx, argument=new_name)
        member = ctx.author

        tag = await self.bot.database.get_tag(name=name)

        if tag is None:
            await ctx.message.delete(delay=10.0)
            message = await ctx.send("Could not find a tag with that name.")
            return await message.delete(delay=10.0)

        if tag.creator_id != ctx.author.id:
            if (not is_admin(member)) or (not is_milind(member)):
                return await ctx.send("You don't have permission to do that.")

        await tag.rename(new_name=new_name)
        await ctx.send("You have successfully renamed your tag.")
        return


async def setup(bot):
    await bot.add_cog(TagCommands(bot))

