import typing

import disnake
from disnake.ext import commands
from disnake.ext.commands import check
from utils.enums import Config

__all = (
    "is_admin_check",
    "is_milind_check",
    "is_mod_check",
    "is_staff_check",
    "is_true_garrixer_check",
    "is_garrixer_check",
    "is_admin",
    "is_milind",
    "is_mod",
    "is_staff",
    "is_true_garrixer",
    "is_garrixer",
)


def is_admin(member: disnake.Member) -> bool:
    """
    This function takes a member ( :class:`disnake.Member` ) object and checks if the member has the admin role or not.
    If the member has the admin role, it will return True, else False.

    Parameters:
        member (disnake.Member): This parameter takes the member object.

    Returns:
        ( bool ): If the member has the role, it will return True, else False.
    """
    for role in member.roles:
        if role.id == Config.ADMIN_ROLE.value:
            return True
    return False


def is_admin_check() -> typing.Callable[[commands.Context, disnake.ApplicationCommandInteraction], bool]:
    """
    A :class:`commands.check` decorator that checks if a user is an admin.
    It takes a :class:`disnake.ApplicationCommandInteraction` ( if the check is used on a slash command decorator ) or
    :class:`commands.Context` ( if it used on a normal prefix command decorator ), and returns a bool.
    If the user is not an admin, it will return False, otherwise it will return True.
    """

    def predicate(
            context: typing.Union[commands.Context, disnake.ApplicationCommandInteraction]
    ) -> bool:
        """
        An inner function that takes a typing.Union[:class:`commands.Context`, :class:`disnake.ApplicationCommandInteraction`] object and returns a bool.

        Parameters:
            context (typing.Union[commands.Context, disnake.ApplicationCommandInteraction]): This parameter takes command data object.

        Returns:
            ( bool ): Returns True, if the specified condition pass in this check, else this function will return False.
        """
        return is_admin(context.author)

    return check(predicate)


def is_milind(member: disnake.Member) -> bool:
    """
    This function checks that if the id of a member ( :class:`disnake.Member` ) is the bot owner id ( 421608483629301772 ).
    If the ID of the member is the ID of the bot owner, then it will True, otherwise it will return False.

    Parameters:
        member (disnake.Member): This parameter takes the member object that needs to be checked.

    Returns:
        ( bool ): If the ID of the member is the ID of the bot owner, then it will True, otherwise it will return False.
    """
    return member.id == 421608483629301772


def is_milind_check() -> typing.Callable[[commands.Context, disnake.ApplicationCommandInteraction], bool]:
    """
    A :class:`commands.check` decorator that checks if a user is the bot owner.
    It takes a :class:`disnake.ApplicationCommandInteraction` ( if the check is used on a slash command decorator ) or
    :class:`commands.Context` ( if it used on a normal prefix command decorator ), and returns a bool.
    If the user is not the bot owner, it will return False, otherwise it will return True.
    """

    def predicate(
            context: typing.Union[commands.Context, disnake.ApplicationCommandInteraction]
    ) -> bool:
        """
        An inner function that takes a typing.Union[:class:`commands.Context`, :class:`disnake.ApplicationCommandInteraction`] object and returns a bool.

        Parameters:
            context (typing.Union[commands.Context, disnake.ApplicationCommandInteraction]): This parameter takes command data object.

        Returns:
            ( bool ): Returns True, if the specified condition pass in this check, else this function will return False.
        """
        return is_milind(context.author)

    return check(predicate)


def is_mod(member: disnake.Member) -> bool:
    """
    This function takes a member ( :class:`disnake.Member` ) object and checks if the member has the mod role or not.
    If the member has the mod role, it will return True, else False.

    Parameters:
        member (disnake.Member): This parameter takes the member object.

    Returns:
        ( bool ): If the member has the role, it will return True, else False.
    """
    for role in member.roles:
        if role.id == Config.MODERATOR_ROLE.value:
            return True
    return is_admin(member)


def is_mod_check() -> typing.Callable[[commands.Context, disnake.ApplicationCommandInteraction], bool]:
    """
    A :class:`commands.check` decorator that checks if a user is a moderator.
    It takes a :class:`disnake.ApplicationCommandInteraction` ( if the check is used on a slash command decorator ) or
    :class:`commands.Context` ( if it used on a normal prefix command decorator ), and returns a bool.
    If the user is not a moderator, it will return False, otherwise it will return True.
    """

    def predicate(
            context: typing.Union[commands.Context, disnake.ApplicationCommandInteraction]
    ) -> bool:
        """
        An inner function that takes a typing.Union[:class:`commands.Context`, :class:`disnake.ApplicationCommandInteraction`] 
        object and returns a bool.

        Parameters:
            context (typing.Union[commands.Context, disnake.ApplicationCommandInteraction]): This parameter takes command data object.

        Returns:
            ( bool ): Returns True, if the specified condition pass in this check, else this function will return False.
        """
        return is_mod(context.author)

    return check(predicate)


def is_staff(member: disnake.Member) -> bool:
    """
    This function takes a member ( :class:`disnake.Member` ) object and checks if the member has the staff role or not.
    If the member has the staff role, it will return True, else False.

    Parameters:
        member (disnake.Member): This parameter takes the member object.

    Returns:
        ( bool ): If the member has the role, it will return True, else False.
    """
    for role in member.roles:
        if role.id == Config.STAFF_ROLE.value:
            return True
    return False


def is_staff_check() -> typing.Callable[[commands.Context, disnake.ApplicationCommandInteraction], bool]:
    """
    A :class:`commands.check` decorator that checks if a user is a staff.
    It takes a :class:`disnake.ApplicationCommandInteraction` ( if the check is used on a slash command decorator ) or
    :class:`commands.Context` ( if it used on a normal prefix command decorator ), and returns a bool.
    If the user is not staff, it will return False, otherwise it will return True.
    """

    def predicate(
            context: typing.Union[commands.Context, disnake.ApplicationCommandInteraction]
    ) -> bool:
        """
        An inner function that takes a typing.Union[:class:`commands.Context`, :class:`disnake.ApplicationCommandInteraction`] object and returns a bool.

        Parameters:
            context (typing.Union[commands.Context, disnake.ApplicationCommandInteraction]): This parameter takes command data object.

        Returns:
            ( bool ): Returns True, if the specified condition pass in this check, else this function will return False.
        """
        return is_staff(member=context.author)

    return check(predicate)


def is_true_garrixer(member: disnake.Member) -> bool:
    """
    This function takes a member ( :class:`disnake.Member` ) object and checks if the member has the true garrixer role or not.
    If the member has the true garrixer role, it will return True, else False.

    Parameters:
        member (disnake.Member): This parameter takes the member object.

    Returns:
        ( bool ): If the member has the role, it will return True, else False.
    """
    for role in member.roles:
        if role.id == Config.TRUE_GARRIXER_ROLE.value:
            return True
    return is_mod(member)


def is_true_garrixer_check() -> typing.Callable[[commands.Context, disnake.ApplicationCommandInteraction], bool]:
    """
    A :class:`commands.check` decorator that checks if a user has the true garrixer role or not.
    It takes a :class:`disnake.ApplicationCommandInteraction` ( if the check is used on a slash command decorator ) or
    :class:`commands.Context` ( if it used on a normal prefix command decorator ), and returns a bool.
    If the user does not have the true garrixer role, it will return False, otherwise it will return True.
    """

    def predicate(context: typing.Union[commands.Context, disnake.ApplicationCommandInteraction]) -> bool:
        """
        An inner function that takes a typing.Union[:class:`commands.Context`, :class:`disnake.ApplicationCommandInteraction`] object and returns a bool.

        Parameters:
            context (typing.Union[commands.Context, disnake.ApplicationCommandInteraction]): This parameter takes command data object.

        Returns:
            ( bool ): Returns True, if the specified condition pass in this check, else this function will return False.
        """
        return is_true_garrixer(context.author)

    return check(predicate)


def is_garrixer(member: disnake.Member) -> bool:
    """
    This function takes a member ( :class:`disnake.Member` ) object and checks if the member has the garrixer role or not.
    If the member has the garrixer role, it will return True, else False.

    Parameters:
        member (disnake.Member): This parameter takes the member object.

    Returns:
        ( bool ): If the member has the role, it will return True, else False.
    """
    for role in member.roles:
        if role.id == Config.GARRIXER_ROLE.value:
            return True
    return is_true_garrixer(member)


def is_garrixer_check() -> typing.Callable[[commands.Context, disnake.ApplicationCommandInteraction], bool]:
    """
    A :class:`commands.check` decorator that checks if a user has the true garrixer role or not.
    It takes a :class:`disnake.ApplicationCommandInteraction` ( if the check is used on a slash command decorator ) or
    :class:`commands.Context` ( if it used on a normal prefix command decorator ), and returns a bool.
    If the user does not have the true garrixer role, it will return False, otherwise it will return True.
    """
    def predicate(context: typing.Union[commands.Context, disnake.ApplicationCommandInteraction]) -> bool:
        """
        An inner function that takes a typing.Union[:class:`commands.Context`, :class:`disnake.ApplicationCommandInteraction`] object and returns a bool.

        Parameters:
            context (typing.Union[commands.Context, disnake.ApplicationCommandInteraction]): This parameter takes command data object.

        Returns:
            ( bool ): Returns True, if the specified condition pass in this check, else this function will return False.
        """
        return is_garrixer(context.author)

    return check(predicate)
