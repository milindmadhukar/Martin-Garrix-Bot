import disnake
import random


def get_eightball_embed(question: str) -> disnake.Embed:
    responses = [
        "As I see it, yes.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don’t count on it.",
        "It is certain.",
        "It is decidedly so.",
        "Most likely.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Outlook good.",
        "Reply hazy, try again.",
        "Signs point to yes.",
        "Very doubtful.",
        "Without a doubt.",
        "Yes.",
        "Yes – definitely.",
        "You may rely on it.",
    ]
    return (
        disnake.Embed(title="The Magic 8 Ball \U0001F3B1 replies")
        .add_field(name="Question", value=question, inline=False)
        .add_field(name="Answer", value=random.choice(responses), inline=False)
    )
