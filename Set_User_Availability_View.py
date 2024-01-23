import discord
import sys
from datetime import datetime, date, time 
sys.path.append(".")
import W2D_Event

ANYTIME_STRING = "Anytime"

select_time_options = [discord.SelectOption(label=ANYTIME_STRING)]
select_time_options += [ discord.SelectOption(label=time(hour=t).strftime("%I:%M %p")) for t in range(24) ]

class Time_Select(discord.ui.Select):
	def __init__(self, placeholder: str, row: int):
		super().__init__(placeholder=placeholder, options=select_time_options, row=row)
		
	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()

class Set_User_Availability_View(discord.ui.View):
	def __init__(self, event_title: str, event_uuid_str: str, user_id: int, date_labels: list[str], e_m: W2D_Event.W2D_Event_Manager, default_time_ranges: list[list[tuple[time, time]]] | None=None):
		super().__init__(timeout=None)
		
		self.starting_time = Time_Select(placeholder="Start time", row=0)
		self.ending_time = Time_Select(placeholder="End time", row=1)
		
		self.add_item(self.starting_time)
		self.add_item(self.ending_time)
		
		self.date_labels = date_labels
		
		self.time_ranges = [ [] for date in date_labels ] if default_time_ranges is None else default_time_ranges
		self.current_selected_date = 0
		self.event_title = event_title
		self.event_uuid_str = event_uuid_str
		self.user_id = user_id
		self.e_m = e_m
		# status should display:
		# event title
		# currently selected date label
		# currently selected time ranges
		# most recent error (if any)
		self.status = ""
		self.error_msg = ""
		self.update_status()
		
	def update_status(self):
		self.status = '''Event: {title}
Availability on {curr_date}
{list_avail}
{err}'''.format(
title=self.event_title, 
curr_date=self.date_labels[self.current_selected_date], 
list_avail="\n".join([ r_i[0].strftime("%I:%M %p") + " - " + r_i[1].strftime("%I:%M %p") for r_i in self.time_ranges[self.current_selected_date]]), 
err=self.error_msg)

	def get_status(self):
		return self.status
		
	@discord.ui.button(label="Reset Day's Availability", row=2, style=discord.ButtonStyle.red)
	async def reset_day(self, interaction:discord.Interaction, button:discord.ui.Button):
		self.time_ranges[self.current_selected_date][:] = []
		
		# clear selections
		self.starting_time.values[:] = []
		self.ending_time.values[:] = []
		
		# update text values
		self.error_msg = f"Reset availability for {self.date_labels[self.current_selected_date]}"
		self.update_status()
		await interaction.response.edit_message(content=self.status, view=self)
		self.error_msg = ""
		
	@discord.ui.button(label="Add time range", row=2)
	async def add_range(self, interaction: discord.Interaction, button: discord.ui.Button):
		# check if entered strings are valid time range
		start = self.starting_time.values
		end = self.ending_time.values
		try:
			# ensure exactly 1 option is selected in each menu
			assert(len(start) == 1)
			assert(len(end) == 1)
			# convert string values to time() objects
			start = time(hour=0) if start[0] == ANYTIME_STRING else datetime.strptime(start[0], "%I:%M %p").time()
			end = time(hour=23) if end[0] == ANYTIME_STRING else datetime.strptime(end[0], "%I:%M %p").time()
			# add range to list of times for selected day
			self.time_ranges[self.current_selected_date].append(tuple([start, end]))
		except:
			self.error_msg = "Please select ONE option for Start time and ONE option for End time"
		
		# clear selections
		self.starting_time.values[:] = []
		self.ending_time.values[:] = []
		# update text values
		self.update_status()
		await interaction.response.edit_message(content=self.status, view=self)
		self.error_msg = ""
		
	@discord.ui.button(label="Cancel", row=4, style=discord.ButtonStyle.red)
	async def cancel_view(self, interaction: discord.Interaction, button: discord.ui.Button):
		# TODO: this should make a popup dialog to confirm
		self.stop()
		self.clear_items()
		await interaction.response.edit_message(content="Set Availability cancelled.", delete_after=30, view=self)
		
	# no need for next/prev buttons if only 1 days TODO?
	@discord.ui.button(custom_id="prev-button", label="Prev", row=4, disabled=True)
	async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
		num_days = len(self.date_labels)
		if self.current_selected_date == num_days-1:
			for i in button.view.children:
				if isinstance(i, discord.ui.Button) and i.custom_id == "next-button":
					i.disabled = False
		
		if self.current_selected_date == 1:
			button.disabled = True
		if self.current_selected_date >= 1:
			self.current_selected_date -= 1
			# clear selections
			self.starting_time.values[:] = []
			self.ending_time.values[:] = []
			# update view status message
			self.update_status()
			await interaction.response.edit_message(content=self.status, view=self)
			
	@discord.ui.button(custom_id="next-button", label="Next", row=4)
	async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.current_selected_date == 0:
			for i in button.view.children:
				if isinstance(i, discord.ui.Button) and i.custom_id == "prev-button":
					i.disabled = False
					
		num_days = len(self.date_labels)
		if self.current_selected_date == num_days-2:
			button.disabled=True
		if self.current_selected_date <= num_days-2:
			self.current_selected_date += 1
			# clear selections
			self.starting_time.values[:] = []
			self.ending_time.values[:] = []
			# update view status message
			self.update_status()
			await interaction.response.edit_message(content=self.status, view=self)
	
	@discord.ui.button(label="Submit", row=4, style=discord.ButtonStyle.green)
	async def submit_view(self, interaction: discord.Interaction, button: discord.ui.Button):
		# TODO: set status message, popup dialog to confirm, then call method from Event_Handler, and gracefully exit
		self.e_m.set_event_attendee_availability(self.event_uuid_str, self.user_id, self.time_ranges)
		self.stop()
		self.clear_items()
		await interaction.response.edit_message(content="Successfully set your availability!", delete_after=30, view=self)
			
			
		
	
	
	

	
