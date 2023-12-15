import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands

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

# Create and implement commands here
@bot.tree.command()
@app_commands.describe(words="The words you input")
async def hello_world(interaction: discord.Interaction, words: str = ""):
	await interaction.response.send_message("HELLO.  :)" + words, ephemeral=True, delete_after=30)

# Start bot
bot.run(TOKEN)
