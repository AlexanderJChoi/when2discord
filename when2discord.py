import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load Environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TESTING_GUILD_ID = os.getenv('TESTING_GUILD_ID')

# Initialize bot and guild
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='w2d!', description='A bot that will help you schedule events!', intents=intents)
my_guild = discord.Object(id=TESTING_GUILD_ID)

# Implement helper functions

# Create and implement commands here
@bot.tree.command(name="hello_world", description="this is a test slash command", guilds=[my_guild])
async def hello_world(ctx):
	await ctx.send("HELLO.  :)")

# Start bot
bot.run(TOKEN)
