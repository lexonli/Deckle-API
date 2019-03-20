from uuid import uuid4

from chalice import Chalice

from chalicelib.db import InMemoryTodoDB


app = Chalice(app_name='mytodo')
app.debug = True
_DB = None
DEFAULT_USERNAME = 'default'


def get_app_db():
    global _DB
    if _DB is None:
        _DB = InMemoryTodoDB()
    return _DB


@app.route('/todos', methods=['GET'])
def get_todos():
    return get_app_db().list_items()


# Following the example get_todos() function, add the rest of the required
# routes here...

@app.route('/todos', methods=['POST'])
def add_new_todo():
    body = app.current_request.json_body
    return get_app_db().add_item(description=body["description"], metadata=body.get('metatdata'), )


@app.route('/todos/{uid}', methods=['GET'])
# remember to pass the parameter in!
def get_todo(uid):
    return get_app_db().get_item(uid)

@app.route('/todos/{uid}', methods=['DELETE'])
def delete_todo(uid):
    return get_app_db().delete_item(uid)

@app.route('/todos/{uid}', methods=['PUT'])
def update_todo(uid):
    body = app.current_request.json_body
    get_app_db().update_item(uid, description=body.get("description"), state=body.get("state"), metadata=body.get("metadata"))






