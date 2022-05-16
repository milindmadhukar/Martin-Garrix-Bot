# Martin Garrix Bot!

A multipurpose bot created exclusively for Garrixers.

![Martin Garrix Bot](https://cdn.discordapp.com/avatars/799613778052382720/28de7ee4e8cc26956e4bf45ecb730b79.webp?size=256 "Martin Garrix Bot")

## 💻 Usage
**To try the bot, join the Martin Garrix Discord Server [here.](https://discord.gg/8sQvsmAT6s)**

## ️️🛠️ Tools Used

This project was written in `Python 3`

The bot was primarily built upon the [disnake](https://github.com/DisnakeDev/disnake) API wrapper, and `Postgres` for the database. `Asyncpg` was used to establish connections to the database.

The bot also uses `YouTube` and `Reddit` APIs for certain functionality.

## ⛏️  Local Setup

To set the project locally, the following steps are to be followed.
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications), create an application. Create a bot and note down the bot's secret token. Go to Ouath, select `bot` and copy the bot invite link with `administrator` previleges.
1. Create a PostgreSQL database and note the database uri down. 
1. Get yourself YouTube API and Reddit API tokens.
1. Create a `.env` file in the root directory of the project and paste the following.
```
TOKEN = "Bot token"

POSTGRES_URI = postgresql://postgres@localhost/<dbname>?user<=username>&password=<password>

REDDIT_CLIENT_ID = "Reddit Client ID"
REDDIT_CLIENT_SECRET = "Reddit Client Secret"

YOUTUBE_API_TOKEN = "Youtube API Token"

ERROR_CHANNEL = <ID Of Channel to send error messages in>
```
1. Create a virtual environment and run `pip install -r requirements.txt` to install all the necessary dependencies for the bot.
2. Edit the `utils/enums.py` file to add values of your own server. Make sure values are correct as it might lead to the bot not working as intended.
3. Run the bot using `python main.py`. The bot should now be running and will automatically create tables in the database if everything was configured correctly.



That's it, have fun ✚✖
