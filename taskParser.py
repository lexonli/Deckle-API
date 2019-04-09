from app import get_app_db
import chalicelib.db as dynamoDB
import csv

db = get_app_db()

with open('Deckle.csv') as f:
	taskReader = csv.reader(f, delimiter=',')
	for task in taskReader:
			name = task[0]
			duration = int(task[1])
			deadlineDateTime = task[2]
			db.add_item(description=name, duration=duration, deadline=deadlineDateTime)
			