from .events import getEvents, createEvent, credentials
from .sort import getNextTask, sortTasks
from datetime import datetime
import time

FORMAT = '%Y-%m-%d %H:%M'
START_OF_DAY = datetime.now()
END_OF_DAY = datetime.now().replace(hour=23, minute=59)

# Timespace object: would most likely receive input of item[1], item[2] of 
# item = (str, str, str): (eventName, startdatetime, enddatetime)
class Timespace:
	# init start time and end time with datetime
	def __init__(self, start=START_OF_DAY, end=END_OF_DAY, task=None):
		self.start = start
		self.end = end
		self.task = task

	def duration(self):
		return self.end - self.start # time delta

	def partition(self, startCut, endCut):
		return (Timespace(start=self.start, end=startCut), 
				Timespace(start=endCut, end=self.end))

def getTimespaces(events):
	"""
	param: List of 3-tuple: (name, startTimeString, endTimeString)
	rtype: List of timespaces
	"""
	# initial timespace
	timespace = Timespace()
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

def allocate(timespaces, listOfTasks):
	sortedTasks = sortTasks(listOfTasks)
	eventTimeSpaces = []
	isLast = False
	for timespace in timespaces:
		hasAvailableTask = True
		while hasAvailableTask:
			info = getNextTask(sortedTasks, timespace.duration())

			# no possible task
			if info == None:
				hasAvailableTask = False
			else:
				matchedTask = info[0]
				taskDuration = info[1] #time delta object
				endTaskDatetime = timespace.start + taskDuration
				eventTimeSpaces.append(Timespace(start=timespace.start, 
													end=endTaskDatetime, task=matchedTask))
				timespace.start = endTaskDatetime
	return eventTimeSpaces

def timespaceToJsonDict(timespace):
	task = timespace.task
	task["start"] = datetime.strftime(timespace.start, FORMAT)
	task["end"] = datetime.strftime(timespace.end, FORMAT)
	return task


def deckleUpdate(eventTimeSpaces):
	deckleList = []
	for eventTimeSpace in eventTimeSpaces:
		deckleList.append(timespaceToJsonDict(eventTimeSpace))
	return deckleList

def createTaskEvents(eventTimeSpaces, creds):
	for eventTimeSpace in eventTimeSpaces:
		createEvent(eventTimeSpace.task["description"], eventTimeSpace.start, eventTimeSpace.end, creds=creds)


if __name__ == '__main__':
	test = [{
        "deadline": "2019-04-06 10:05",
        "description": "find the milk",
        "duration": 30.0,
        "metadata": {},
        "state": "unstarted",
        "uid": "a0779206-90e8-4d4a-8be2-fb948859143d",
        "username": "default"
    }, 
    {
        "deadline": "2019-04-08 12:05",
        "description": "find the chocolate",
        "duration": 40.0,
        "metadata": {},
        "state": "unstarted",
        "uid": "d3243346-90e8-4d4a-8be2-fb948853433d",
        "username": "default"
    },
    {
        "deadline": "2019-04-12 14:05",
        "description": "find the teddy bear",
        "duration": 60.0,
        "metadata": {},
        "state": "unstarted",
        "uid": "bgd3346-90e8-4d4a-8be2-fb948853433d",
        "username": "default"
    }]
	events = getEvents()
	timespaces = getTimespaces(events)
	eventTimeSpaces = allocate(timespaces, test)
	print(deckleUpdate(eventTimeSpaces))
	# createTaskEvents(eventTimeSpaces, credentials())

