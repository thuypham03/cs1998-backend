from asyncio import Task
import json
from pydoc import describe
from flask import Flask, request
import db

app = Flask(__name__)

DB = db.DatabaseDriver()

@app.route("/")
@app.route("/tasks/")
def get_tasks():
    """
    Endpoint for getting all tasks
    """
    return json.dumps({"tasks": DB.get_all_tasks()}), 200


@app.route("/tasks/", methods=["POST"])
def create_task():
    """
    Endpoint for creating a task
    """
    body = json.loads(request.data)
    description = body.get("description")
    task_id = DB.insert_task_table(description, False)
    task = DB.get_task_by_id(task_id)

    if task is None:
        return json.dumps({"error": "Something went wrong while creating task!"}), 400
    return json.dumps(task), 200


@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    """
    Endpoint for getting task by id
    """
    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found"}), 404
    return json.dumps(task), 200


@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    """
    Endpoint for updating task by id
    """
    body = json.loads(request.data)
    desciption = body.get("description")
    done = body.get("done")

    DB.update_task_by_id(task_id, desciption, done)

    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found"}), 404
    return json.dumps(task), 200


@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    """
    Endpoint for deleting a task by id
    """
    task = DB.get_task_by_id(task_id)
    if task is None:
        return json.dumps({"error": "Task not found"}), 404
    DB.delete_task_by_id(task_id)
    return json.dumps(task), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
