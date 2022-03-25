from dataclasses import dataclass
from errno import ESOCKTNOSUPPORT
import json
from wsgiref.util import request_uri
from flask import Flask, request
import db
from datetime import datetime

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
        return failure_response("Something went wrong while creating user!", 400)
    
    user["transactions"] = []
    return success_response(user, 201)

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting user by id
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    user["transactions"] = DB.get_transactions_by_user_id(user_id)
    return success_response(user)

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deletting a user by id
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found")
    user["transactions"] = DB.get_transactions_by_user_id(user_id)
    
    DB.delete_user_by_id(user_id)
    DB.delete_transactions_by_id(user_id)
    return success_response(user)

@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    """
    Endpoint for creating a transaction
    """
    body = json.loads(request.data)
    timestamp = datetime.timestamp(datetime.now())
    sender_id = body.get("sender_id", -1)
    receiver_id = body.get("receiver_id", -1)
    amount = body.get("amount", -1)
    message = body.get("message", -1)
    accepted = body.get("accepted", None)

    if sender_id == -1 or receiver_id == -1 or amount == -1 or message == -1:
        return failure_response("Missing transaction detail", 400)

    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if sender is None or receiver is None:
        return failure_response("User not found")
    
    if accepted == True:
        if amount > sender.get("balance"):
            return failure_response("Amount exceed sender's balance", 403)
        DB.update_user_by_id(sender_id, sender.get("balance") - amount)
        DB.update_user_by_id(receiver_id, receiver.get("balance") + amount)
    
    transaction_id = DB.insert_transactions_table(timestamp, sender_id, receiver_id, amount, message, accepted)
    transaction = DB.get_transaction_by_id(transaction_id)

    return success_response(transaction, 201)

@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def update_transaction(transaction_id):
    """
    Endpoint for updating (accept/ deny) a transaction
    """
    body = json.loads(request.data)
    timestamp = datetime.timestamp(datetime.now())
    accepted = body.get("accepted", -1)
    if accepted == -1:
        return failure_response("Missing request detail", 400)

    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return failure_response("Transaction not found")

    if transaction.get("accepted") is not None:
        return failure_response("Cannot change transaction", 403)
    
    if accepted == False:
        DB.update_transaction_by_id(transaction_id, timestamp, accepted)
    else:
        sender_id = transaction.get("sender_id")
        receiver_id = transaction.get("receiver_id")
        amount = transaction.get("amount")

        sender = DB.get_user_by_id(sender_id)
        receiver = DB.get_user_by_id(receiver_id)
        
        if amount > sender.get("balance"):
            return failure_response("Amount exceed sender's balance", 403)

        DB.update_user_by_id(sender_id, sender.get("balance") - amount)
        DB.update_user_by_id(receiver_id, receiver.get("balance") + amount)
        DB.update_transaction_by_id(transaction_id, timestamp, accepted)

    transaction = DB.get_transaction_by_id(transaction_id)
    return success_response(transaction)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
