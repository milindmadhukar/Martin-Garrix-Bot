import disnake
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
    for role in member.roles:
        if role.id == Config.ADMIN_ROLE.value:
            return True
    return False


def is_admin_check():
    def predicate(ctx) -> bool:
        return is_admin(ctx.author)

    return check(predicate)


def is_milind(member: disnake.Member) -> bool:
    return member.id == 421608483629301772


def is_milind_check():
    def predicate(ctx) -> bool:
        return is_milind(ctx.author)

    return check(predicate)


def is_mod(member: disnake.Member) -> bool:
    for role in member.roles:
        if role.id == Config.MODERATOR_ROLE.value:
            return True
    return is_admin(member)


def is_mod_check():
    def predicate(ctx) -> bool:
        return is_mod(ctx.author)

    return check(predicate)


def is_staff(member: disnake.Member) -> bool:
    for role in member.roles:
        if role.id == Config.STAFF_ROLE.value:
            return True
    return False


def is_staff_check():
    def predicate(ctx) -> bool:
        return is_staff(ctx.author)

    return check(predicate)


def is_true_garrixer(member: disnake.Member) -> bool:
    for role in member.roles:
        if role.id == Config.TRUE_GARRIXER_ROLE.value:
            return True
    return is_mod(member)


def is_true_garrixer_check():
    def predicate(ctx) -> bool:
        return is_true_garrixer(ctx.author)

    return check(predicate)


def is_garrixer(member: disnake.Member) -> bool:
    for role in member.roles:
        if role.id == Config.GARRXIER_ROLE.value:
            return True
    return is_true_garrixer(member)


def is_garrixer_check():
    def predicate(ctx) -> bool:
        return is_garrixer(ctx.author)

    return check(predicate)
