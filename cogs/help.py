import discord
from discord.ext import commands
import itertools

class HelpCommand(commands.HelpCommand):
    def custom_embed(self, **kwargs):
        return discord.Embed(color=discord.Colour.teal(), **kwargs).set_footer(text=f"Called by: {self.context.author}")

    def command_desk(self, command: commands.Command, add_example=False):
        if command.help:
            _help, *example = command.help.split("\nexample:\n")
        else:
            _help, example = "No specified description.", None

        desk = "%s```dust\n%s```" % (
            _help,
            self.clean_prefix
            + command.qualified_name
            + " "
            + command.signature.translate(str.maketrans("[]", "{}")),
        )
        if add_example and example:
            desk += "**Example**```md\n%s```" % example[0]

        return desk

    @property
    def opening_note(self):
       return f"Use `{self.clean_prefix}help [command]` for more info on a command.\n You can also use `{self.clean_prefix}help [category]` for more info on a category."

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f'Command "{command.qualified_name}" has no subcommand named "{string}".'
        return f'Command "{command.qualified_name}" has no subcommands.'

    @staticmethod
    def __get_cog(command: commands.Command):
        cog = command.cog
        return cog.qualified_name if cog else "No Category"

    async def send_bot_help(self, mapping):
        embed = self.custom_embed(title=f"{self.context.bot.user.name} Help.", description=self.opening_note)
        embed.set_thumbnail(url=self.context.bot.user.avatar_url)
        bot_commands = await self.filter_commands(
            self.context.bot.commands, sort=True, key=self.__get_cog
        )

        for category, cmds in itertools.groupby(bot_commands, key=self.__get_cog):
            embed.add_field(
                name=category,
                value="```\n%s```" % ", ".join(cmd.name for cmd in cmds),
                inline=False,
            )

        await self.context.send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        embed = self.custom_embed(title=cog.qualified_name, description=cog.description)
        for command in cog.get_commands():
            embed.add_field(
                name=" | ".join([command.name] + command.aliases),
                value=self.command_desk(command),
                inline=False,
            )

        return await self.context.send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        if group.name in ['config']:
            return await self.context.invoke(group)
        embed = self.custom_embed(
            title=" | ".join([group.name] + group.aliases),
            description=self.command_desk(group),
        )
        for command in group.commands:
            embed.add_field(
                name=" | ".join([command.name] + command.aliases),
                value=self.command_desk(command),
                inline=False,
            )

        return await self.context.send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        if command.name in ['leaderboard', 'quiz']:
            return await self.context.invoke(command)

        embed = self.custom_embed(title=" | ".join([command.name] + command.aliases),
                                      description=self.command_desk(command, add_example=True))
        return await self.context.send(embed=embed)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self
        bot.get_command("help").hidden = True
    
def setup(bot):
    bot.add_cog(Help(bot))

