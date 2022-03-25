import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores it into the
        instance variable 'conn'
        """
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_users_table()

    def create_users_table(self):
        """
        Using SQL, creates a user table
        """
        try:
            self.conn.execute(
                """
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL,
                        balance INTEGER
                    );
                """
            )
        except Exception as e:
            print(e)

    def get_all_users(self):
        cursor = self.conn.execute("SELECT * FROM users;")
        users = []

        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        
        return users

    def insert_users_table(self, name, username, balance):
        """
        Using SQL, adds a new user to the user table
        """
        cursor = self.conn.execute(
            """
            INSERT INTO users (name, username, balance)
            VALUES (?, ?, ?)
            """, (name, username, balance)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, id):
        """
        Using SQL, gets a user by its id
        """
        cursor = self.conn.execute("SELECT * FROM users WHERE id=?", (id,))

        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        
        return None
    
    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user by its id
        """
        self.conn.execute("DELETE FROM users WHERE id=?", (id,))
        self.conn.commit()

    def update_user_by_id(self, id, balance):
        """
        Using SQL, updates a user's balance by its id
        """
        self.conn.execute("UPDATE users SET balance=? WHERE id=?", (balance, id))
        self.conn.commit()

DatabaseDriver = singleton(DatabaseDriver)