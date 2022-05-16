import os
import sys

from core.MartinBotBase import MartinGarrixBot

if __name__ == "__main__":
    bot = MartinGarrixBot()
    bot.load_cogs(["cogs"])
    try:
        bot.run(os.getenv("TOKEN"))
    except KeyboardInterrupt:
        print("[*] Exiting.......")
        sys.exit(0)
