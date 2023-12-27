from datetime import date, time, timezone
from copy import deepcopy
import uuid

# Converts a 'time' Object to an integer representing the number of half hours since 12AM
# returns an integer between 0 and 47 inclusive
def time_to_int(t: time, round_up: bool=True):
	int_t = (t.hour * 2)
	if t.minute >= 30:
		if round_up:
			int_t += 2
		else:
			int_t += 1
	elif t.minute > 0 and round_up:
		int_t += 1
		
	return int_t if int_t <= 48 else 48

# Converts an integer to a 'time' Object
# returns the time, if i is the number of half hours since 12AM
def int_to_time(i: int):
	return time(hour= i/2, minute= (i%2) * 30)

# Stores time ranges as binary
# Can reconstruct equivalent time ranges
class Availability:
	def __init__(self, times: list[tuple[time,time]] | int =0):
		self.stored_bin_times = 0
		if isinstance(times, int):
			self.stored_bin_times = times
		else:
			self.stored_bin_times = self.get_bin_availability(times)
		
	def __del__(self):
		del self.stored_bin

	def get_bin_availability(self, times: list[tuple[time,time]] | None =None):
		if times is None:
			return self.stored_bin_times
			
		bin_times: int = 0
		for t in times:
			begin = time_to_int(t[0])
			end = time_to_int(t[1], round_up=False)
			for i in range(begin, end):
				bin_times |= (1 << i)
		return bin_times
		
	def get_range_availability(self, bin_times: int | None =None):
		if bin_times is None:
			bin_times = self.stored_bin_times
			
		range_times: list[tuple[time,time]] = []
		i = 0
		begin_time = None
		while i < 48:
			if begin_time is None and bin_times & (1 << i):
				begin_time = int_to_time(i)
			if begin_time is not None and not bin_times & (1 << i):
				range_times.append(tuple([begin_time, int_to_time(i)]))
				begin_time = None
			i += 1
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
	# m * n runtime (m attendees, n days)
	def get_group_availability(self, availabilities: dict[int, dict[date, int]] | None):
		if availabilities is None:
			availabilities = self.attendees_availability
		
		group_availability = dict[date, int]
		for attendee_id in availabilities:
			attendee_availability = availabilities[attendee_id]
			for date_id in attendee_availability:
				if date_id in group_availability:
					group_availability[date_id] &= attendee_availability[date_id]
				else:
					group_availability[date_id] = attendee_availability[date_id]
					
		return group_availability
		
	# adding attendee availability data
	def set_attendee_availability(self, attendee_id: int, attendee_availability: dict[date,int] | dict[date,Availability]):
		if isinstance(attendee_availability, dict[date,int]):
			self.attendees_availability[attendee_id] = deepcopy(attendee_availability)
			return
		elif isinstance(attendee_availability, dict[date,Availability]):
			bin_attendee_availability = dict[date, int]
			for date_id in attendee_availability:
				bin_attendee_availability[date_id] = attendee_availability[date_id].get_bin_availability()
			elf.attendees_availability[attendee_id] = deepcopy(bin_attendee_availability)
			return
		
	# getting attendee availability data
	def get_attendee_availability(self, attendee_id: int):
		if attendee_id in self.attendees_availability:
			return deepcopy(self.attendees_availability[attendee_id])
		else:
			return dict[date, int]
