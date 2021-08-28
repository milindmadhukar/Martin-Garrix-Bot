# Martin Garrix Bot!

A multipurpose bot created exclusively for Garrixers.

![Martin Garrix Bot](https://cdn.discordapp.com/avatars/799613778052382720/28de7ee4e8cc26956e4bf45ecb730b79.webp?size=256 "Martin Garrix Bot")

_Please note that this bot is unfinished, a lot of code is unoptimized, not linted or formatted and I am archiving the project since the development of the module [discord.py](https://github.com/Rapptz/discord.py)  until I find time to rewrite it in some other module/language._

## 💻 Usage
**To invite the bot and try it yourself click [here.](https://milindm.me/bot-invite)**

## ️️🛠️ Tools Used

This project was written in `Python 3`

The bot was primarily built upon the [discord.py](https://github.com/Rapptz/discord.py) module, and `Postgres` for the database. `Asyncpg` was used to establish connections to the database.

The bot also uses `YouTube` and `Reddit` APIs for certain functionality.

## ⛏️  Local Setup

To set the project locally, the following steps are to be followed.
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications), create an application. Create a bot and note down the bot's secret token. Go to Ouath, select `bot` and copy the bot invite link with `administrator` previleges.
1. Create a PostgreSQL database and note the database uri down. 
1. Get yourself Youtube API and Reddit API tokens.
1. Create a `.env` file in the root directory of the project and paste the following.
```
TOKEN = <bot's secret token from discord developer portal>
POSTGRES_URI = postgresql://postgres@localhost/databasename?user=username&password=password
REDDIT_CLIENT_ID = <reddit client id>
REDDIT_CLIENT_SECRET = <reddit client secret>
YOUTUBE_API_TOKEN = <youtube api token>
ERROR_CHANNEL = <channel id to report errors>
```
1. Create a virtual environment and run `pip install -r requirements.txt` to install all the necessary dependencies for the bot.
1.Run the bot using `python main.py`. The bot should now be running and will automatically create tables in the database if everything was configured correctly.


*If you invited the bot to a server before running the bot, it will cause errors, make sure to invite the bot only after you ran it so that it can make necessary entries in the database.*

#### Extras
If you face any difficulties contact me [here.](https://milindm.me/contact/)

Thats it, have fun ✚✖