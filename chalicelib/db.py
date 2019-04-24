from uuid import uuid4

from boto3.dynamodb.conditions import Key


DEFAULT_USERNAME = 'default'
DEFAULT_DURATION = 25 #MINUTES
DEFAULT_DEADLINE = '01-01-2200 10:00'


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


# class InMemoryTodoDB(TodoDB):
#     def __init__(self, state=None):
#         if state is None:
#             state = {}
#         self._state = state

#     def list_all_items(self):
#         all_items = []
#         for username in self._state:
#             all_items.extend(self.list_items(username))
#         return all_items

#     def list_items(self, username=DEFAULT_USERNAME):
#         return self._state.get(username, {}).values()

#     def add_item(self, description, metadata=None, username=DEFAULT_USERNAME, 
#                 duration=DEFAULT_DURATION, deadline=DEFAULT_DEADLINE):
#         if username not in self._state:
#             self._state[username] = {}
#         uid = str(uuid4())
#         self._state[username][uid] = {
#             'uid': uid,
#             'description': description,
#             'state': 'unstarted',
#             'duration': duration,
#             'deadline': deadline,
#             'metadata': metadata if metadata is not None else {},
#             'username': username
#         }
#         return uid

#     def get_item(self, uid, username=DEFAULT_USERNAME):
#         return self._state[username][uid]

#     def delete_item(self, uid, username=DEFAULT_USERNAME):
#         del self._state[username][uid]

#     def update_item(self, uid, description=None, state=None,
#                     metadata=None, username=DEFAULT_USERNAME, 
#                     duration=None, deadline=None):
#         item = self._state[username][uid]
#         if description is not None:
#             item['description'] = description
#         if state is not None:
#             item['state'] = state
#         if metadata is not None:
#             item['metadata'] = metadata
#         if duration is not None:
#             item['duration'] = duration
#         if deadline is not None:
#             item['deadline'] = deadline


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

    def add_item(self, description, username, metadata=None, 
                duration=DEFAULT_DURATION, deadline=DEFAULT_DEADLINE):
        uid = str(uuid4())
        self._table.put_item(
            Item={
                'username': username,
                'uid': uid,
                'description': description,
                'duration': duration,
                'deadline': deadline,
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
                    metadata=None, duration=None, deadline=None):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(uid, username)
        if description is not None:
            item['description'] = description
        if state is not None:
            item['state'] = state
        if metadata is not None:
            item['metadata'] = metadata
        if duration is not None:
            item['duration'] = duration
        if deadline is not None:
            item['deadline'] = deadline
        self._table.put_item(Item=item)
