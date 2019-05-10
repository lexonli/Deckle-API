import logging
from datetime import datetime, timedelta

import pytz
from uuid import uuid4

from .events import getEvents, credentials
from .sort import getNextTask, sortTasks
# from events import getEvents, credentials
# from sort import getNextTask, sortTasks

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FORMAT = '%Y-%m-%d %H:%M'
URL_FORMAT = '%Y-%m-%d-%H-%M'

# Timespace object: would most likely take in arguments of item[1], item[2] of 
# item = (str, str, str): (eventName, startdatetime, enddatetime)
class Timespace:
	# init start time and end time with datetime
	def __init__(self, start, end, task=None):
		self.start = start
		self.end = end
		# name of the task
		self.task = task

	@classmethod
	def asEvent(cls, event, username):
		task = {}
		# obtain start and end datetimes
		start = datetime.strptime(event[1], FORMAT)
		end = datetime.strptime(event[2], FORMAT)

		# create task data
		task["deadline"] = event[2] #note: we're setting deadline as the end datetime string
		task["metadata"] = {}
		task["username"] = username
		task["description"] = event[0]
		duration_delta = end - start
		task["duration"] = duration_delta.seconds // 60
		task["uid"] = str(uuid4())
		task["state"] = "event"
		task["priority"] = 0
		task["deck"] = "event"
		task["startline"] = event[1]

		return cls(start=start, end=end, task=task)

	@classmethod
	def asBreak(cls, timespace, username):
		task = {}

		start = timespace.start
		end = timespace.end

		task["deadline"] = datetime.strftime(end, FORMAT)
		task["metadata"] = {}
		task["username"] = username
		task["description"] = "break"
		duration_delta = end - start
		task["duration"] = duration_delta.seconds // 60
		task["uid"] = str(uuid4())
		task["state"] = "break"
		task["priority"] = 0
		task["deck"] = "break"
		task["startline"] = datetime.strftime(start, FORMAT)

		return cls(start=start, end=end, task=task)


	def duration(self):
		return self.end - self.start # time delta

	def partition(self, startCut, endCut):
		return (Timespace(start=self.start, end=startCut), 
				Timespace(start=endCut, end=self.end))

def getTimespaces(events, currentDateTime, days):
	"""
	param: List of 3-tuple: (name, startTimeString, endTimeString)
	rtype: List of timespaces
	"""
	days = int(days)
	# initial timespace
	startDateTime = datetime.strptime(currentDateTime, URL_FORMAT)
	logger.info(startDateTime)
	timespace = Timespace(start=startDateTime, end=(startDateTime + timedelta(days=days)).replace(hour=23, minute=59))
	timespaces = []
	if events:
		# make sure events are sorted
		# events.sort(key=lambda x: x[1])
		logger.info(events)
		print(events)
		# generate timespaces
		for event in events:
			eventStart = datetime.strptime(event[1], FORMAT)
			eventEnd = datetime.strptime(event[2], FORMAT)
			# create two timespaces by partitioning start to end
			twoTimespaces = timespace.partition(eventStart, eventEnd)
			timespaces.append(twoTimespaces[0])
			timespace = twoTimespaces[1]
	# append the last timespace
	timespaces.append(timespace)
	return timespaces


def allocate(timespaces, listOfTasks, events, username):
	# events.sort(key=lambda x: x[1])
	sortedTasks = sortTasks(listOfTasks)
	eventTimeSpaces = []
	isLast = False
	for timespace in timespaces:
		hasAvailableTask = True
		while hasAvailableTask:
			info = getNextTask(sortedTasks, timespace.duration())

			# no possible task that fits the timespace
			if info == None:
				hasAvailableTask = False
				# if the final slot in that timespace has space, we make it into a break
				if timespace.start < timespace.end:
					eventTimeSpaces.append(Timespace.asBreak(timespace, username))
				# append the event into the list
				if events:
					eventTimeSpaces.append(Timespace.asEvent(events.pop(0), username))
			else:
				matchedTask = info[0]
				taskDuration = info[1] #time delta object
				endTaskDatetime = timespace.start + taskDuration
				eventTimeSpaces.append(Timespace(start=timespace.start, 
													end=endTaskDatetime, task=matchedTask))
				# change timespace start time
				timespace.start = endTaskDatetime
	while events:
		eventTimeSpaces.append(Timespace.fromEvent(events.pop(0)))
	return eventTimeSpaces

def timespaceToDeckle(timespace):
	task = timespace.task
	task["start"] = datetime.strftime(timespace.start, FORMAT)
	task["end"] = datetime.strftime(timespace.end, FORMAT)
	return task


def deckleUpdate(eventTimeSpaces):
	deckleList = []
	for eventTimeSpace in eventTimeSpaces:
		deckleList.append(timespaceToDeckle(eventTimeSpace))
	return deckleList



if __name__ == '__main__':
	events = getEvents()
	timespaces = getTimespaces(events)
	eventTimeSpaces = allocate(timespaces, test)
	print(deckleUpdate(eventTimeSpaces))

