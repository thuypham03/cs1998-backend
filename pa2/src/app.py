from dataclasses import dataclass
import json
from wsgiref.util import request_uri
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)

def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({'error': message}), code

@app.route("/")
def hello_world():
    return "Hello world!"

@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all users
    """
    return success_response({"users": DB.get_all_users()})

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    name = body.get("name", -1)
    username = body.get("username", -1)
    balance = body.get("balance", 0)

    if name == -1 or username == -1:
        return failure_response("Missing name or username", 400)

    user_id = DB.insert_users_table(name, username, balance)
    user = DB.get_user_by_id(user_id)

    if user is None:
        return failure_response("Something went wrong while creating task!", 400)
    return success_response(user, 201)

@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting user by id
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    return success_response(user)

@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deletting a user by id
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    
    DB.delete_user_by_id(user_id)
    return success_response(user)

@app.route("/api/send/", methods=["POST"])
def send_money():
    """
    Endpoint for sending money from one user to another
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id", -1)
    receiver_id = body.get("receiver_id", -1)
    amount = body.get("amount", -1)

    if sender_id == -1 or receiver_id == -1 or amount == -1:
        return failure_response("Missing request information", 400)

    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if sender is None or receiver is None:
        return failure_response("User not found")

    if amount > sender.get("balance"):
        return failure_response("Amount exceed sender's balance", 400)

    DB.update_user_by_id(sender_id, sender.get("balance") - amount)
    DB.update_user_by_id(receiver_id, receiver.get("balance") + amount)

    return success_response(body)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
