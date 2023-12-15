import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord-ui import SlashInteraction, UI

# Load Environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TESTING_GUILD_ID = os.getenv('TESTING_GUILD_ID')

# Initialize bot and ui extension
bot = commands.Bot(" ")
ui = UI(bot)

# Implement helper functions

# Create and implement commands here
@ui.slash.command("hello world", description="this is a test slash command", options=[
		SlashOption(str, name="test_string", description="this parameter will be printed")
		], guild_ids=[TESTING_GUILD_ID])
async def hello_world(ctx, test_string="walk!!!"):
	await ctx.respond("HELLO. YOU SAID: " + str(test_string) + " :)")

# Start bot
bot.run(TOKEN)
