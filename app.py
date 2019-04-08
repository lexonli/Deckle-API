from chalice import Chalice
from chalicelib import db, sort, events, deckleManager, auth
import os
import boto3

app = Chalice(app_name='mytodo')
app.debug = True
_DB = None
_VERSION = "0.1"
_DUMMY = False
TOKENFILE = "token.json"
AUTHFILE = "authentication.json"
BUCKET = "deckle-data"

def dummy():
    """
    Dummy function to force chalice to autogen a policy with all the permissions required.

    Uncomment the ones you really need
    Some S3 function help is here: https://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html
    """
    s3 = boto3.client('s3')
    s3.download_file()
    s3.get_bucket_region()
    s3.get_bucket_location()
    s3.get_object()
    s3.head_bucket()
    s3.head_object()
    s3.list_objects_v2()
    s3.list_buckets()
    s3.put_object()
    s3.delete_object()
    db = boto3.resource('dynamodb')
    db.list_items()
    db.Table()
    db.scan()
    db.query()
    db.put_item()
    db.get_item()
    db.delete_item()
    

def get_app_db():
    global _DB
    if _DB is None:
        _DB = db.DynamoDBTodo(
            boto3.resource('dynamodb').Table(
                os.environ['APP_TABLE_NAME'])
            )
    return _DB


@app.route('/')
def index():
    """
    Calling the root / provides a simple response of the a json object with
    'service': app.app_name, 
    'version': _VERSION
    """
    if _DUMMY:
        dummy()
    return {'service': app.app_name, 'version': _VERSION}


@app.route('/todos/decklelist', methods=['GET'])
def update_calendar():
    eventsList = events.getEvents(BUCKET, TOKENFILE)
    timespaces = deckleManager.getTimespaces(eventsList)
    tasks = get_app_db().list_items()
    eventTimeSpaces = deckleManager.allocate(timespaces, tasks)
    deckleList = deckleManager.deckleUpdate(eventTimeSpaces)
    return deckleList

@app.route('/todos/auth', methods=['GET'])
def authenticate_user():
    return auth.requestToAuthServer(AUTHFILE)

@app.route('/todos/poll', methods=['POST'])
def poll_server():
    body = app.current_request.json_body
    pollData = auth.pollToAuthServer(BUCKET, AUTHFILE, TOKENFILE, body)
    return {"message": "polling successful"}

@app.route('/todos/refresh', methods=['GET'])
def refresh():
    auth.refreshAccessTokenToAuthServer(BUCKET, TOKENFILE, AUTHFILE)
    return {"message": "access token refreshed"}

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


