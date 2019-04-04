import datetime

FORMAT = '%Y-%m-%d %H:%M'
START = datetime.datetime.strptime("2019-01-01 00:00", FORMAT)

def sortTasks(listOfTasks):
	tasks = []
	for task in listOfTasks:
		deadline = datetime.datetime.strptime(task["deadline"], FORMAT)
		diffInSeconds = (deadline - START).total_seconds()
		score = diffInSeconds
		tasks.append((score, task))
	sortedTasks = sorted(tasks)
	return [item[1] for item in sortedTasks]

def getNextTask(sortedTasks, realDuration):
    for task in sortedTasks:
        durationDelta = datetime.timedelta(minutes=int(task["duration"]))
        if realDuration > durationDelta:
            sortedTasks.remove(task)
            return (task, durationDelta)
    return None


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
	sortTasks(test)
