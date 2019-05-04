from uuid import uuid4
from chalice import BadRequestError
from datetime import datetime

from boto3.dynamodb.conditions import Key


DEFAULT_DURATION = 25 #MINUTES
DEFAULT_DEADLINE = '01-01-2200 10:00'
DEFAULT_STARTLINE = '01-04-2019 10:00'
FORMAT = '%Y-%m-%d %H:%M'


class TodoDB(object):
    def list_items(self):
        pass

    def add_item(self, description, metadata=None):
        pass

    def get_item(self, uid):
        pass

    def delete_item(self, uid):
        pass

    def update_item(self, uid, description=None, state=None,
                    metadata=None):
        pass

def validate_startline_deadline(startline, deadline):
    start_date = datetime.strptime(startline, FORMAT)
    end_date = datetime.strptime(deadline, FORMAT)
    if start_date >= end_date:
        raise BadRequestError("item's startline is later or same as deadline")


class DynamoDBTodo(TodoDB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, username):
        response = self._table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        return response['Items']

    def add_item(self, description, username, startline = DEFAULT_STARTLINE, metadata=None, 
                duration=DEFAULT_DURATION, deadline=DEFAULT_DEADLINE, priority=0, deck="miscellaneous"):
        validate_startline_deadline(startline, deadline)
        uid = str(uuid4())
        self._table.put_item(
            Item={
                'username': username,
                'uid': uid,
                'description': description,
                'duration': duration,
                'startline': startline,
                'deadline': deadline,
                'priority': priority,
                'deck': deck,
                'state': 'unstarted',
                'metadata': metadata if metadata is not None else {},
            }
        )
        return uid


    def get_item(self, uid, username):
        try:
            response = self._table.get_item(
                Key={
                    'username': username,
                    'uid': uid,
                },
            )
        except:
            response = None
        # return response['Item']
        return response


    def delete_item(self, uid, username):
        self._table.delete_item(
            Key={
                'username': username,
                'uid': uid,
            }
        )


    def update_item(self, uid, username, description=None, state=None,
                    metadata=None, duration=None, deadline=None, startline=None, priority=None, deck=None):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(uid, username)
        if description is not None:
            item["Item"]['description'] = description
        if state is not None:
            item["Item"]['state'] = state
        if metadata is not None:
            item["Item"]['metadata'] = metadata
        if duration is not None:
            item["Item"]['duration'] = duration
        if priority is not None:
            item["Item"]['priority'] = priority
        if deck is not None:
            item["Item"]['deck'] = deck
        if deadline is not None and startline is not None:
            validate_startline_deadline(startline, deadline)
            item["Item"]['startline'] = startline
            item["Item"]['deadline'] = deadline
        elif deadline is not None:
            validate_startline_deadline(item["Item"]["startline"], deadline)
            item["Item"]['deadline'] = deadline
        elif startline is not None:
            validate_startline_deadline(startline, item["Item"]["deadline"])
            item["Item"]['startline'] = startline
        self._table.put_item(Item=item["Item"])


    def update_all_items(self, username, description=None, state=None,
                        metadata=None, duration=None, deadline=None, startline=None, priority=None, deck=None):
        items = self.list_items(username)
        for item in items:
            self.update_item(
                uid=item["uid"], 
                username=username, 
                description=description, 
                state=state,
                metadata=metadata,
                duration=duration,
                deadline=deadline,
                startline=startline,
                priority=priority,
                deck=deck)
                            

