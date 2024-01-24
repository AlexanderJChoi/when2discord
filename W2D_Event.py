from datetime import date, time, timezone, timedelta
from copy import deepcopy
import pickle
import uuid
import os


# TODO: should keep track of user -> timezone mapping (either per event, or in a file managed by Event Manager)

# TODO: need method for breaking up a message into parts

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
	return time(hour= i//2, minute= (i%2) * 30) # the // operator is "floored division"
	
# Return a list of dates between two dates
def generate_date_list_from_range(d1: date, d2: date):
	if d2 < d1: 
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

# converts dict[date, int] to dict[str, str] in a nice way
def event_availability_to_readable(event_availability: dict[date, int], range_delim: str=" "):
	dates = list(event_availability.keys())
	availability_ints = list(event_availability.values())
	
	dates_str = [ d.strftime("%A %B %d %Y") for d in dates]
	availability_ranges = [ range_delim.join([ ranges[0].strftime("%I:%M %p") + " - " + ranges[1].strftime("%I:%M %p")  for ranges in Availability(date_availability).get_range_availability() ]) for date_availability in availability_ints]
	return dict(zip(dates_str, availability_ranges))

# Implement W2D_Event
class W2D_Event:
	def __init__(self, title: str, group_id: int, selected_days: list[date], earliest_time: time, latest_time: time, selected_timezone: timezone or None=None):
		self.title = title
		self.group_id = group_id
		self.selected_days = selected_days
		self.earliest_time = earliest_time
		self.latest_time = latest_time
		self.selected_timezone = selected_timezone
		self.event_uuid = uuid.uuid4()
		# maps discord user/member id to user's availability info
		# may be useful to have a class for availability_dict later
		self.attendees_availability: dict[int, dict[date, int]] = dict()
		
	# need methods for 
	# getting plausible_event_times
	# m * n runtime (m attendees, n days)
	def get_group_availability(self, availabilities: dict[int, dict[date, int]] | None=None):
		if availabilities is None:
			availabilities = self.attendees_availability
		
		group_availability: dict[date, int] = dict()
		for attendee_id in availabilities:
			attendee_availability = availabilities[attendee_id]
			for date_id in attendee_availability:
				if date_id in group_availability:
					group_availability[date_id] &= attendee_availability[date_id]
				else:
					group_availability[date_id] = attendee_availability[date_id] & Availability([(self.earliest_time, self.latest_time)]).get_bin_availability()
					
		return group_availability
		
	# adding attendee availability data
	def set_attendee_availability(self, attendee_id: int, attendee_availability: dict[date,int] | dict[date,Availability]):
		if len(attendee_availability) == 0:
			# set to NOT AVAILABLE
			self.attendees_availability[attendee_id] = dict(zip(self.selected_days , [0 for day in self.selected_days]))
			return
		# test whether dictionary values are int or Availability 
		test = list(attendee_availability.values())[0]
		if isinstance(test, int):
			self.attendees_availability[attendee_id] = deepcopy(attendee_availability)
			return
		elif isinstance(test, Availability):
			bin_attendee_availability: dict[date, int] = dict()
			for date_id in attendee_availability:
				bin_attendee_availability[date_id] = attendee_availability[date_id].get_bin_availability()
			elf.attendees_availability[attendee_id] = deepcopy(bin_attendee_availability)
			return
		
	# getting attendee availability data
	def get_attendee_availability(self, attendee_id: int):
		if attendee_id in self.attendees_availability:
			return deepcopy(self.attendees_availability[attendee_id])
		else:
			return dict()
			
	# TODO: transfer to json format; requires method for checking if files are already pickled, and translate them to json
			
	# writes W2D_Event as binary into file
	def dump_to_file(self):
		filename = str(self.title) + "." + str(self.event_uuid) + ".w2de"
		with open(filename, 'wb') as f:
			f.write(pickle.dumps(self))

	# read W2D_Event from file as binary
	def load_from_file(filename):
		with open(filename, 'rb') as f:
			return pickle.load(f)


class W2D_Event_Manager:
	def __init__(self):
		self.uuid_to_event: dict[str, W2D_Event] = dict()
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
	
	def create_event(self, title: str, group_id: int, date_begin: date, date_end: date, earliest_time: time, latest_time: time) :
		days = generate_date_list_from_range(date_begin, date_end)
		new_event = W2D_Event(title=title, group_id=group_id, selected_days=days, earliest_time=earliest_time, latest_time=latest_time)
		new_event_uuid_str = str(new_event.event_uuid)
		new_event.dump_to_file()
		self.uuid_to_event[new_event_uuid_str] = new_event
		return new_event_uuid_str
	
	def is_event(self, event_uuid_str: str):
		return event_uuid_str in self.uuid_to_event
		
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
		if self.is_event(uuid_str):
			return self.uuid_to_event[uuid_str]
		return None
		
	def get_event_info(self, uuid_str: str):
		e = self.get_event(uuid_str)
		if e is None:
			return None
		s = '''Event: {title} : {event_uuid}
		--------------------------------------------------
		Earliest Time: {e_time} Latest Time: {l_time}
		Suggested Days: {days}
		Attendees User IDs ({n}): {attendees}'''.format(title=e.title, event_uuid=str(e.event_uuid), e_time=e.earliest_time.strftime("%I:%M %p"), l_time=e.latest_time.strftime("%I:%M %p"), days=str("\n".join([ day.strftime("%A %B %d %Y") for day in e.selected_days] )), n=len(e.attendees_availability), attendees=str("\n".join(e.attendees_availability)))
		return s
		
		
	def get_group_events(self, group_id: int):
		return [ e for e in self.uuid_to_event.values() if e.group_id == group_id ]
		
	def get_group_event_list(self, group_id: int):
		events = [ (e.title, str(e.event_uuid), len(e.attendees_availability)) for e in self.get_group_events(group_id) ] 
		info = list(zip(*events))
		return list(info[0]), list(info[1]), list(info[2])
		
	def get_group_event_list_str(self, group_id: int):
		return "\n".join([ f"{e.title} : {str(e.event_uuid)} : {len(e.attendees_availability)} attendees" for e in self.get_group_events(group_id) ])
		
	# ()
	# viewing event data (total availabiilty, all users availability, specific user's availability)
	# modifying event parameters
	# modifying specific user's availability
	
	# should load event once, then keep in memory
	# but also save immediately after each change.
	
	
	# TZ TODO: this should translate times from user tz to event tz
	def set_event_attendee_availability(self, event_uuid_str : str, attendee_id: int, attendee_availability: list[list[tuple[time, time]]]):
		e = self.get_event(event_uuid_str)
		d = dict()
		for day, ranges in zip(e.selected_days, attendee_availability):
			day_availability = Availability(ranges)
			d[day] = day_availability.get_bin_availability()
		e.set_attendee_availability(attendee_id, d)
		e.dump_to_file()
	
	# TZ TODO: this should translate times from event tz to user tz
	def get_selected_event_days_times(self, event_uuid_str: str):
		e = self.get_event(event_uuid_str)
		return [ day.strftime("%A %B %d %Y") for day in e.selected_days] , [(e.earliest_time, e.latest_time)]
		
	def is_event_attendee(self, event_uuid_str: str, attendee_id: int):
		return self.is_event(event_uuid_str) and attendee_id in self.get_event(event_uuid_str).attendees_availability.keys()
		
	def get_event_attendee_availability(self, event_uuid_str : str, attendee_id: int):
		if not self.is_event_attendee(event_uuid_str, attendee_id):
			return None
		e = self.get_event(event_uuid_str)
		attendee_availability = e.get_attendee_availability(attendee_id)
		return [ Availability(date_availability).get_range_availability() for date_availability in list(attendee_availability.values()) ] 
	
	def get_event_title(self, event_uuid_str: str):
		e = self.get_event(event_uuid_str)
		if e is None: 
			return None
		return e.title
		
	def get_event_group_availability(self, event_uuid_str: str):
		e = self.get_event(event_uuid_str)
		if e is None:
			return dict()
		e_readable = event_availability_to_readable(e.get_group_availability())
		filtered_keys = [ key for key in list(e_readable.keys()) if not e_readable[key] == ""]
		filtered_values = [value for value in list(e_readable.values()) if not value == ""]
		return filtered_keys, filtered_values
		
	def reset_event_attendee_availability(self, event_uuid_str : str, attendee_id: int):
		e = self.get_event(event_uuid_str)
		if e is None:
			return
		e.attendees_availability.pop(attendee_id, None)
		e.dump_to_file()
	
if __name__ == '__main__':
	em = W2D_Event_Manager()
	for e_uuid_str in em.uuid_to_event:
		print (len(em.get_event_info(e_uuid_str)))
	print (em.get_group_event_list(559289815636639755))
