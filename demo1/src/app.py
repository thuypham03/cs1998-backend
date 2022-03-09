import json

from flask import Flask
from flask import request
from sqlalchemy import false

app = Flask(__name__)

tasks = {
    0: {
        "id": 0,
        "description": "laundry",
        "done": False
    },
    1: {
        "id": 1,
        "description": "homework",
        "done": False
    }
}

task_id_counter = 2

@app.route("/")
def hello():
    return "Hello Sophia!"

@app.route("/tasks/")
def get_tasks():
    """
    Retrieve all tasks
    """
    res = {"task": list(tasks.values())}
    return json.dumps(res), 200

@app.route("/tasks/", methods=["POST"])
def create_task():
    """
    Create new task
    """
    global task_id_counter
    body = json.loads(request.data)
    description = body["description"]
    task = {"id": task_id_counter, "description": description, "done": False}
    tasks[task_id_counter] = task
    task_id_counter += 1
    return json.dumps(task), 201

@app.route("/tasks/<int:task_id>/")
def get_task(task_id):
    """
    Retrieve task by task_id
    """
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"error": "Task not found"}), 404
    return json.dumps(task), 200

@app.route("/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    """
    Update task by task_id
    """
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"error": "Task not found"}), 404
    body = json.loads(request.data)
    task["description"] = body["description"]
    task["done"] = body["done"]
    return json.dumps(task), 200

@app.route("/tasks/<int:task_id>/", methods=["DELETE"])
def delete_task(task_id):
    """
    Delete task with task_id
    """
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"error": "Task not found"}), 404
    del tasks[task_id]
    return json.dumps(task), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


# pip3 install -r src/requirements.txt
