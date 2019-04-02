"""
receive list of dictionaries, where each dictionary contains task information
"""
from datetime import datetime

START = datetime.strptime("01-01-2019 00:00", "%d-%m-%Y %H:%M")

def sortTasks(listOfTasks):
	tasks = []
	for task in listOfTasks:
		deadline = datetime.strptime(task["deadline"], "%d-%m-%Y %H:%M")
		diffInSeconds = (deadline - START).total_seconds()
		score = diffInSeconds
		tasks.append((score, task))
	sortedTasks = sorted(tasks)
	return sortedTasks

def getTaskUid(sortedTasks, realDuration):
	for scoredTask in sortedTasks:
		if realDuration > scoredTask[1]["duration"]:
			return scoredTask[1]["uid"]
	return None


if __name__ == '__main__':
	test = [{
        "deadline": "06-04-2019 10:05",
        "description": "find the milk",
        "duration": 30.0,
        "metadata": {},
        "state": "unstarted",
        "uid": "a0779206-90e8-4d4a-8be2-fb948859143d",
        "username": "default"
    }, 
    {
        "deadline": "08-04-2019 10:05",
        "description": "find the chocolate",
        "duration": 40.0,
        "metadata": {},
        "state": "unstarted",
        "uid": "d3243346-90e8-4d4a-8be2-fb948853433d",
        "username": "default"
    },
    {
        "deadline": "01-04-2019 10:05",
        "description": "find the teddy bear",
        "duration": 60.0,
        "metadata": {},
        "state": "unstarted",
        "uid": "bgd3346-90e8-4d4a-8be2-fb948853433d",
        "username": "default"
    }]
	sortTasks(test)
