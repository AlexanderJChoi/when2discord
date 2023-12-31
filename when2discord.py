import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime, time

# Import local modules
import sys
sys.path.append(".")
import Switching_View

# Load Environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TESTING_GUILD_ID = os.getenv('TESTING_GUILD_ID')

my_guild = discord.Object(id=TESTING_GUILD_ID)

# Define Bot
class MyBot(commands.Bot):
	async def setup_hook(self):
		self.tree.copy_global_to(guild=my_guild)
		await self.tree.sync(guild=my_guild)

# Initialize bot
intents = discord.Intents.default()
bot = MyBot(command_prefix='w2d!', description='A bot that will help you schedule events!', intents=intents)

# Implement helper functions

# Implement Data Transformers
class TimeTransformer(app_commands.Transformer):
	async def transform(self, interaction: discord.Interaction, value: str) -> time:
		tv = datetime.strptime(value, "%I:%M%p")
		return tv.time()

# Handle any errors
@bot.tree.error
async def on_command_error(interaction: discord.Interaction, error):
	if isinstance(error, app_commands.TransformerError):
		await interaction.response.send_message(f"COMMAND {interaction.command.name} FAILED. COULD NOT TRANSFORM VALUE {error.value}. INCORRECT FORMAT.", ephemeral=True, delete_after=30)

# Create and implement commands here
@bot.tree.command()
@app_commands.describe(words="The words you input")
async def hello_world(interaction: discord.Interaction, words: str = ""):
	await interaction.response.send_message("HELLO.  :)" + words, ephemeral=True, delete_after=30)
	
# TODO: write better description of expected time format
@bot.tree.command()
@app_commands.describe(name="The name of this event", 
	no_earlier_than_time="The earliest time the event might begin (format like: 10:31PM or 10:31pm)", 
	no_later_than_time="The latest time the event might end (format like: 10:31PM or 10:31pm)",
	timezone="The event's local timezone. This parameter does nothing in the current version.")
@app_commands.rename(no_earlier_than_time="no_earlier_than",
	no_later_than_time="no_later_than")
async def create_event(interaction: discord.Interaction, name: str, no_earlier_than_time: app_commands.Transform[time, TimeTransformer], no_later_than_time: app_commands.Transform[time, TimeTransformer], timezone: str or None=None):
	group_id = interaction.guild_id
	message = f"{name} : {str(no_earlier_than_time)} : {str(no_later_than_time)} : {str(group_id)}"
	ephemeral = False
	if no_later_than_time < no_earlier_than_time:
		message="ERROR no_later_than must be after no_earlier_than"
		ephemeral=True
	# TODO: create a View for adding date intervals
	await interaction.response.send_message(message, ephemeral=ephemeral)

# Testing Switching_View
@bot.tree.command()
async def try_switching_view(interaction: discord.Interaction):
	await interaction.response.send_message(content="TESTING SWITCHING VIEW", ephemeral=True, view=Switching_View.Switching_View())

# Start bot
bot.run(TOKEN)
