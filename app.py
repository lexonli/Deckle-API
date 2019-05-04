from chalice import Chalice, AuthResponse, BadRequestError
from chalicelib import db, sort, events, deckleManager, googleAuth, auth
import os
import boto3
import logging

### tasks response schema reference
# [{'deadline': '2019-4-29 10:0', 'metadata': {}, 'username': 'default', 'description': 'COMP 3 Week 5 SVMs and decision boundaries Practical', 'duration': Decimal('60'), 'uid': '0a04e54d-b77d-4fcb-8dd5-57b607c74c2e', 'state': 'unstarted', 'startline':'2019-01-04 10:00'}]
# i.e. array of json objects with columns: 
# "deadline", "metadata", "username", "description", "duration", "uid", "state"

### /decklelist response schema reference
# array of json objects with columns: 
# "deadline", "metadata", "username", "description", "duration", "uid", "state", "start", "end"

app = Chalice(app_name='mytodo')
app.debug = True
_DB = None
_USER_DB = None
_VERSION = "0.1"
_DUMMY = False
# old google auth keys
# TOKENFILE = "token.json"
# AUTHFILE = "authentication.json"
BUCKET = "deckle-data"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

def get_users_db():
    global _USER_DB
    if _USER_DB is None:
        _USER_DB = boto3.resource('dynamodb').Table(
            os.environ['USERS_TABLE_NAME'])
    return _USER_DB


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

@app.route('/login', methods=['POST'])
def login():
    body = app.current_request.json_body
    try:
        record = get_users_db().get_item(Key={'username': body['username']})['Item']
        jwt_token = auth.get_jwt_token(body['username'], body['password'], record)
        # The following is throwing `ValueError: Circular reference detected` runtime error
        # return {"token": jwt_token}
        # changed to
        return jwt_token.decode("utf-8")
    except KeyError:
        raise BadRequestError("No such user in the database.")


@app.authorizer()
def jwt_auth(auth_request):
    token = auth_request.token
    decoded = auth.decode_jwt_token(token)
    return AuthResponse(routes=['*'], principal_id=decoded['sub'])
        

def get_authorized_username(current_request):
    return current_request.context['authorizer']['principalId']

@app.route('/todos/decklelist/{startDateTime}', methods=['POST'], authorizer=jwt_auth)
def get_decklelist(startDateTime):
    body = app.current_request.json_body
    username = get_authorized_username(app.current_request)

    tasks = get_app_db().list_items(username=username)

    eventsList = events.getEventsFromJSON(body)
    timespaces = deckleManager.getTimespaces(eventsList, startDateTime)

    eventTimeSpaces = deckleManager.allocate(timespaces, tasks, eventsList, username)
    deckleList = deckleManager.deckleUpdate(eventTimeSpaces)
    return deckleList

# Basic Deckle task operation resources
#assuming authorizer is working using root credentials from local computer
@app.route('/todos', methods=['GET'], authorizer=jwt_auth)
def get_todos():
    username = get_authorized_username(app.current_request)
    return get_app_db().list_items(username=username)


@app.route('/todos', methods=['POST'], authorizer=jwt_auth)
def add_new_todo():
    body = app.current_request.json_body
    username = get_authorized_username(app.current_request)
    try:
        return get_app_db().add_item(
            username = username,
            description=body['description'],
            metadata=body.get('metadata'),
            duration = body['duration'],
            deadline = body['deadline'],
            startline = body['startline'],
            priority = body['priority'],
            deck = body['deck']
        )
    except TypeError:
        raise BadRequestError("Not enough arguments for adding item")


@app.route('/todos/{uid}', methods=['GET'], authorizer=jwt_auth)
def get_todo(uid):
    username = get_authorized_username(app.current_request)
    return get_app_db().get_item(uid, username=username)


@app.route('/todos/{uid}', methods=['DELETE'], authorizer=jwt_auth)
def delete_todo(uid):
    username = get_authorized_username(app.current_request)
    return get_app_db().delete_item(uid, username=username)


@app.route('/todos/{uid}', methods=['PUT'], authorizer=jwt_auth)
def update_todo(uid):
    body = app.current_request.json_body
    username = get_authorized_username(app.current_request)
    get_app_db().update_item(
        uid,
        description=body.get('description'),
        state=body.get('state'),
        metadata=body.get('metadata'),
        duration = body.get('duration'),
        deadline = body.get('deadline'),
        startline = body.get('startline'),
        priority = body.get('priority'),
        deck = body.get('deck'),
        username=username)
    return {"message": "Success: updated"}

@app.route('/todos/all', methods=['PUT'], authorizer=jwt_auth)
def update_all_todos():
    body = app.current_request.json_body
    username = get_authorized_username(app.current_request)
    get_app_db().update_all_items(
        description=body.get('description'),
        state=body.get('state'),
        metadata=body.get('metadata'),
        duration = body.get('duration'),
        deadline = body.get('deadline'),
        startline = body.get('startline'),
        priority = body.get('priority'),
        deck = body.get('deck'),
        username=username)
    return {"message": "Success: updated all"}


# get method for /decklelist using google auth (deprecated)

# @app.route('/todos/decklelist/{startDateTime}', methods=['GET'], authorizer=jwt_auth)
# def update_calendar(currentDateTime):
#     username = get_authorized_username(app.current_request)
#     eventsList = events.getEvents(BUCKET, TOKENFILE)
#     timespaces = deckleManager.getTimespaces(eventsList, currentDateTime)
#     tasks = get_app_db().list_items(username=username)
#     eventTimeSpaces = deckleManager.allocate(timespaces, tasks)
#     deckleList = deckleManager.deckleUpdate(eventTimeSpaces)
#     return deckleList

# google authentication resources (deprecated)

# @app.route('/todos/auth', methods=['GET'], authorizer=jwt_auth)
# def authenticate_user():
#     return googleAuth.requestToAuthServer(AUTHFILE)

# @app.route('/todos/poll', methods=['POST'], authorizer=jwt_auth)
# def poll_server():
#     body = app.current_request.json_body
#     pollData = googleAuth.pollToAuthServer(BUCKET, AUTHFILE, TOKENFILE, body)
#     return {"message": "polling successful"}

# @app.route('/todos/refresh', methods=['GET'], authorizer=jwt_auth)
# def refresh():
#     googleAuth.refreshAccessTokenToAuthServer(BUCKET, TOKENFILE, AUTHFILE)
#     return {"message": "access token refreshed"}


if __name__ == '__main__':
    print(update_calendar())
