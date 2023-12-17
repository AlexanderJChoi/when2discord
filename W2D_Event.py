from datetime import date, time, timezone
from copy import deepcopy
import uuid

# Stores time ranges as binary
# Can reconstruct equivalent time ranges
class Availability:
	def __init__(self, times: list[tuple[time,time]] | int =0):
		self.stored_bin_times = 0
		if isinstance(times, int):
			self.stored_bin_times = times
		else:
			self.stored_bin_times = get_bin_availability(times)
		
	def __del__(self):
		del self.stored_bin

	def get_bin_availability(times: list[tuple[time,time]] | None =None):
		if times is None:
			return self.stored_bin_times
			
		bin_times: int = 0
		# TODO:
		return bin_times
		
	def get_range_availability(bin_times: int | None =None):
		if bin_times is None:
			bin_times = self.stored_bin_times
			
		range_times: list[tuple[time,time]] = []
		# TODO:
		return range_times

# Implement W2D_Event
class W2D_Event:
	def __init__(self, title: str, group_id: int, selected_days: list[date], earliest_time: time, latest_time: time, selected_timezone: timezone):
		self.title = title
		self.selected_days = selected_days
		self.earliest_time = earliest_time
		self.latest_time = latest_time
		self.selected_timezone = selected_timezone
		
		self.event_uuid = uuid.uuid4()
		self.attendees_availability: dict[int, dict[date, int]] # maps discord user/member id to user's availability info
																# may be useful to have a class for availability_dict later
																
	def __del__(self):
		del self.title
		del self.selected_days
		del self.earliest_time
		del self.latest_time
		del self.selected_timezone
		
		del self.event_uuid
		del self.attendees_availability
		
	# need methods for 
	# getting plausible_event_times
	def get_group_availability():
		group_availability = Availability()
		# TODO:
		return group_availability
		
	# adding attendee availability data
	def set_attendee_availability(attendee_id: int, attendee_availability: dict[date,int] | Availability):
		if isinstance(attendee_availability, dict):
			# TODO
			return
		elif isinstance(attendee_availability, Availability):
			# TODO
			return
		
	# getting attendee availability data
	def get_attendee_availability(attendee_id: int):
		# TODO:
		return Availability()
