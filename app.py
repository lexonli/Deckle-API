from chalice import Chalice
from chalicelib import db, sort, events, deckleManager
import os
import boto3

app = Chalice(app_name='mytodo')
app.debug = True
_DB = None

def get_app_db():
    global _DB
    if _DB is None:
        _DB = db.DynamoDBTodo(
            boto3.resource('dynamodb').Table(
                os.environ['APP_TABLE_NAME'])
            )
    return _DB

# TODO:
# This currently does not work, outh authentication is prompted when running it in lambda
@app.route('/todos/decklelist', methods=['GET'])
def update_calendar():
    eventsList = events.getEvents()
    timespaces = deckleManager.getTimespaces(eventsList)
    tasks = get_app_db().list_items()
    eventTimeSpaces = deckleManager.allocate(timespaces, tasks)
    deckleList = deckleManager.deckleUpdate(eventTimeSpaces)
    return deckleList


@app.route('/todos', methods=['GET'])
def get_todos():
    return get_app_db().list_items()


@app.route('/todos', methods=['POST'])
def add_new_todo():
    body = app.current_request.json_body
    return get_app_db().add_item(
        description=body['description'],
        metadata=body.get('metadata'),
        duration = body['duration'],
        deadline = body['deadline']
    )


@app.route('/todos/{uid}', methods=['GET'])
def get_todo(uid):
    return get_app_db().get_item(uid)


@app.route('/todos/{uid}', methods=['DELETE'])
def delete_todo(uid):
    return get_app_db().delete_item(uid)


@app.route('/todos/{uid}', methods=['PUT'])
def update_todo(uid):
    body = app.current_request.json_body
    get_app_db().update_item(
        uid,
        description=body.get('description'),
        state=body.get('state'),
        metadata=body.get('metadata'),
        duration = body.get('duration'),
        deadline = body.get('deadline'))


