from datetime import date, time, timezone, timedelta
from copy import deepcopy
import pickle
import uuid
import os

# TODO: should keep track of user -> timezone mapping (either per event, or in a file managed by Event Manager)

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
	
# Return a list of dates between two dates
def generate_date_list_from_range(d1: date, d2: date):
	if d2 > d1: 
		swap(d1, d2)
	one_day = timedelta(days=1)
	list_of_days = []
	while d1 <= d2:
		list_of_days += [d1]
		d1 += one_day
	return list_of_days

# Returns the date ranges described by the list d
def generate_date_ranges_from_list(d: list[date]):
	sort(d)
	one_day = timedelta(days=1)
	first = d[0]
	prev = d[0]
	ranges = []
	for x in d:
		if x == prev or x == prev + one_day:
			prev = x
		else:
			ranges += [(first, prev)]
			first = x
			prev = x
	return ranges

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
	def __init__(self, title: str, group_id: int, selected_days: list[date], earliest_time: time, latest_time: time, selected_timezone: timezone or None):
		self.title = title
		self.selected_days = selected_days
		self.earliest_time = earliest_time
		self.latest_time = latest_time
		self.selected_timezone = selected_timezone
		
		self.event_uuid = uuid.uuid4()
		
		# maps discord user/member id to user's availability info
		# may be useful to have a class for availability_dict later
		self.attendees_availability: dict[int, dict[date, int]] 

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
			
	# writes W2D_Event as binary into file
	def dump_to_file(self):
		filename = str(self.title) + "." + str(self.event_uuid) + ".w2de"
		with open(filename, 'wb') as f:
			f.write(pickle.dumps(self))

	# read W2D_Event from file as binary
	def load_from_file(filename):
		with open(filename, 'rb') as f:
			return pickle.load(f.read())


class W2D_Event_Manager:
	def __init__(self):
		self.uuid_to_event: dict[str, W2D_Event]
		self.load_event_files()
		
	def load_event_files(self):
		for file_name in os.listdir('.'):
			if file_name.endswith(".w2de"):
				title, uuid_str , post = file_name.split(".", 2)
				# TODO: try catch exceptions for the unpickling
				e = W2D_Event.load_from_file(file_name)
				# verify the file naming convention matches the file data
				if e.title == title and str(e.event_uuid) == uuid_str:
					self.uuid_to_event[uuid_str] = e
	
	def create_event(self, title: str, guild_id: int, date_begin: date, date_end: date, earliest_time: time, latest_time: time) :
		new_event = W2D_Event(title=title, guild_id=guild_id, selected_days= generate_date_list_from_range(date_begin, date_end), earliest_time=earliest_time, latest_time=latest_time)
		new_event_uuid_str = str(new_event.event_uuid)
		new_event.dump_to_file()
		self.uuid_to_event[new_event_uuid_str] = new_event
		return new_event_uuid_str
	
	# should have queue for modifying events
	# i.e. each write action for an event should have an associated queue_write 
	# which simply adds the function, and all required paramaters to the queue
	# then the event manager should have a separate thread/process
	# that handles these queued function calls in order
	# (technically overkill, we only need one queue per event to prevent weird problems)
	# although this doesn't in itself prevent all weird problems
	# and technically weird problems only occur for duplicates modification calls for the same
	# (event, user) pair. Seems unlikely and a low priority.
	
	# needs functions for:
	# finding Event using uuid
	def get_event(self, uuid_str: str): # TODO: do we need to actually return the event, or just uuid/title?
		if uuid_str in self.uuid_to_event:
			return self.uuid_to_event[uuid_str]
		return None
		
	def get_guild_events(self, guild_id: int):
		return [ e for e in self.uuid_to_event.values() if e.guild_id == guild_id ]
		
	# ()
	# viewing event data (total availabiilty, all users availability, specific user's availability)
	# modifying event parameters
	# modifying specific user's availability
	
	# should load event once, then keep in memory
	# but also save immediately after each change.
