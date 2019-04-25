from .events import getEvents, credentials
from .sort import getNextTask, sortTasks
# from events import getEvents, credentials
# from sort import getNextTask, sortTasks
import logging
from datetime import datetime
import time
import pytz

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
	def fromEvent(cls, event, username):
		task = {}
		start = datetime.strptime(event[1], FORMAT)
		end = datetime.strptime(event[2], FORMAT)
		task["deadline"] = event[2]
		task["metadata"] = {}
		task["username"] = username
		task["description"] = event[0]
		durationDelta = end - start
		task["duration"] = durationDelta.seconds // 60
		# maybe we should generate a uuid for events as well?
		task["uid"] = event[0] + event[1] + event[2]
		task["state"] = "event"

		return cls(start=start, end=end, task=task)

	def duration(self):
		return self.end - self.start # time delta

	def partition(self, startCut, endCut):
		return (Timespace(start=self.start, end=startCut), 
				Timespace(start=endCut, end=self.end))

def getTimespaces(events, currentDateTime):
	"""
	param: List of 3-tuple: (name, startTimeString, endTimeString)
	rtype: List of timespaces
	"""
	# initial timespace
	startDateTime = datetime.strptime(currentDateTime, URL_FORMAT)
	logger.info(startDateTime)
	timespace = Timespace(start=startDateTime, end=startDateTime.replace(hour=23, minute=59))
	timespaces = []
	if events:
		# make sure events are sorted
		events.sort(key=lambda x: x[1])
		# generate timespaces
		for event in events:
			eventStart = datetime.strptime(event[1], FORMAT)
			eventEnd = datetime.strptime(event[2], FORMAT)
			twoTimespaces = timespace.partition(eventStart, eventEnd)
			timespaces.append(twoTimespaces[0])
			timespace = twoTimespaces[1]
	# append the last timespace
	timespaces.append(timespace)
	return timespaces


def allocate(timespaces, listOfTasks, events, username):
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
				# append an event into the list
				if events:
					print("appending")
					eventTimeSpaces.append(Timespace.fromEvent(events.pop(0), username))
			else:
				matchedTask = info[0]
				taskDuration = info[1] #time delta object
				endTaskDatetime = timespace.start + taskDuration
				eventTimeSpaces.append(Timespace(start=timespace.start, 
													end=endTaskDatetime, task=matchedTask))
				timespace.start = endTaskDatetime
	while events:
		print("appending again")
		eventTimeSpaces.append(Timespace.fromEvent(events.pop(0)))
	return eventTimeSpaces

def timespaceToJsonDict(timespace):
	task = timespace.task
	task["start"] = datetime.strftime(timespace.start, FORMAT)
	task["end"] = datetime.strftime(timespace.end, FORMAT)
	return task


def deckleUpdate(eventTimeSpaces):
	print(eventTimeSpaces)
	deckleList = []
	for eventTimeSpace in eventTimeSpaces:
		deckleList.append(timespaceToJsonDict(eventTimeSpace))
	return deckleList

def createTaskEvents(eventTimeSpaces, creds):
	for eventTimeSpace in eventTimeSpaces:
		createEvent(eventTimeSpace.task["description"], eventTimeSpace.start, eventTimeSpace.end, creds=creds)


if __name__ == '__main__':
	events = getEvents()
	timespaces = getTimespaces(events)
	eventTimeSpaces = allocate(timespaces, test)
	print(deckleUpdate(eventTimeSpaces))

