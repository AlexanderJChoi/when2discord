import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime, time, date

import traceback

# Import local modules
import sys
sys.path.append(".")
import Switching_View
import W2D_Event
import Set_User_Availability_View

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

# Initialize Event Manager
e_m = W2D_Event.W2D_Event_Manager()

# Initialize bot
intents = discord.Intents.default()
bot = MyBot(command_prefix='w2d!', description='A bot that will help you schedule events!', intents=intents)

# Implement helper functions

# Implement Data Transformers
class TimeTransformer(app_commands.Transformer):
	async def transform(self, interaction: discord.Interaction, value: str) -> time:
		tv = datetime.strptime(value, "%I:%M %p")
		return tv.time()
	
class DateTransformer(app_commands.Transformer):
	async def transform(self, interaction: discord.Interaction, value: str) -> date:
		dv = datetime.strptime(value, "%d/%m/%Y")
		return dv.date()

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
# TODO: another command to add more date ranges to the event
@bot.tree.command()
@app_commands.describe(name="The name of this event", 
	no_earlier_than_time="The earliest time the event might begin (format like: 10:31 PM or 10:31 pm)", 
	no_later_than_time="The latest time the event might end (format like: 10:31 PM or 10:31 pm)",
	timezone="The event's local timezone. This parameter does nothing in the current version.",
	date_range_begin="The first date in the range to consider (format: DD/MM/YYYY)",
	date_range_end="The last date in the range to consider (format: DD/MM/YYYY)")
@app_commands.rename(no_earlier_than_time="no_earlier_than",
	no_later_than_time="no_later_than")
async def create_event(interaction: discord.Interaction, name: str, date_range_begin: app_commands.Transform[date, DateTransformer], date_range_end: app_commands.Transform[date, DateTransformer], no_earlier_than_time: app_commands.Transform[time, TimeTransformer], no_later_than_time: app_commands.Transform[time, TimeTransformer], timezone: str or None=None):
	group_id = interaction.guild_id
	message = ""
	ephemeral = False
	delete_after = None
	uuid_str =""

	if no_later_than_time < no_earlier_than_time:
		message="ERROR no_later_than must be after no_earlier_than"
		ephemeral=True
		delete_after = 30
	elif date_range_end < date_range_begin:
		message="ERROR date_range_end must be after date_range_begin"
		ephemeral=True
		delete_after = 30
	else:
		uuid_str = e_m.create_event(title=name, group_id=group_id, date_begin=date_range_begin, date_end=date_range_end, earliest_time=no_earlier_than_time, latest_time=no_later_than_time)
		message=f"Event `{name}` created with uuid `{uuid_str}` in guild `{group_id}`"
	
	await interaction.response.send_message(message, ephemeral=ephemeral, delete_after=delete_after)
	
# TODO: any command that requires a event uuid as input should have an autocomplete for both uuid or the title

@bot.tree.command()
async def get_event_info(interaction: discord.Interaction, event_uuid: str):
	message = e_m.get_event_info(event_uuid) # this method returns too many characters. (max 2000 per message)
	if message is None:
		message = f"Event with UUID `{event_uuid}` not found!"
	
	await interaction.response.send_message(message, ephemeral=True)
	
@bot.tree.command()
async def get_event_list(interaction:discord.Interaction):
	group_id = interaction.guild_id
	await interaction.response.send_message(e_m.get_group_event_list(group_id), ephemeral=True)
	
@bot.tree.command()
async def set_my_availability(interaction: discord.Interaction, event_uuid: str):
	# Default message parameters
	view = None
	message = "ERROR"
	
	# check validity of user_entered uuid
	if e_m.is_event(event_uuid):
		try:
			event_title = e_m.get_event_title(event_uuid)
			user_id = interaction.user.id
			date_labels, suggested_time_ranges = e_m.get_selected_event_days_times(event_uuid)
			default_availability = e_m.get_event_attendee_availability(event_uuid, user_id)
			view = Set_User_Availability_View.Set_User_Availability_View(event_title, event_uuid, user_id, date_labels, e_m, default_time_ranges=default_availability)
			message = view.get_status()
		except:
			t, e, tb = sys.exc_info()
			message = str((t, e, tb))
			print(message)
			traceback.print_tb(tb, file=sys.stdout) 
	try:
		await interaction.response.send_message(content=message, ephemeral=True, view=view)
	except:
		print (str(sys.exc_info()))

# TODO: view group availability as image

@bot.tree.command()
async def get_group_availability(interaction: discord.Interaction, event_uuid: str):
	message = "NO such event"
	
	if e_m.is_event(event_uuid):
		try:
			event_title = e_m.get_event_title(event_uuid)
			days, times = e_m.get_event_group_availability(event_uuid)
			if len(days) == 0:
				message = "No times available for event :("
			else:
				message = [f"Availability for {event_title}"] + [ d + ":  " + t for d, t in zip(days, times)]
				message = "\n".join(message)
		except:
			t, e, tb = sys.exc_info()
			message = str((t, e, tb))
			print(message)
			traceback.print_tb(tb, file=sys.stdout) 
	
	await interaction.response.send_message(content=message)

# Testing Switching_View
@bot.tree.command()
async def try_switching_view(interaction: discord.Interaction):
	await interaction.response.send_message(content="TESTING SWITCHING VIEW", ephemeral=True, view=Switching_View.Switching_View())

# Start bot
bot.run(TOKEN)
