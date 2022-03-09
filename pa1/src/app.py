import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

posts = {
    0: {
      "id": 0,
      "upvotes": 1,
      "title": "My cat is the cutest!",
      "link": "https://i.imgur.com/jseZqNK.jpg",
      "username": "alicia98",
    },
    1: {
      "id": 1,
      "upvotes": 3,
      "title": "Cat loaf",
      "link": "https://i.imgur.com/TJ46wX4.jpg",
      "username": "alicia98",
    }
}

comments = {
  0: {
    0: {
      "id": 0,
      "upvotes": 8,
      "text": "Wow, my first Reddit gold!",
      "username": "alicia98"
    }
  }
}

post_id_counter = 2
comment_id_counter = 1

def false_input(para):
  return type(para) != str or para == ""

@app.route("/")
def hello_world():
    return "Hello world!"

@app.route("/api/posts/")
def get_posts():
    """
    Retrieve all posts
    """
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200

@app.route("/api/posts/", methods=["POST"])
def create_post():
  """
  Create new post
  """
  global post_id_counter
  body = json.loads(request.data)
  post = {
    "id": post_id_counter,
    "upvotes": 1,
    "title": body["title"],
    "link": body["link"],
    "username": body["username"]
  }
  posts[post_id_counter] = post
  post_id_counter += 1
  return json.dumps(post), 201

@app.route("/api/extra/posts/", methods=["POST"])
def create_post_extra():
  """
  Create new post
  """
  global post_id_counter
  body = json.loads(request.data)
  if (false_input(body["title"]) or false_input(body["link"]) or false_input(body["username"])):
    return json.dumps({"error": "Invalid request"}), 401

  post = {
    "id": post_id_counter,
    "upvotes": 1,
    "title": body["title"],
    "link": body["link"],
    "username": body["username"]
  }
  posts[post_id_counter] = post
  post_id_counter += 1
  return json.dumps(post), 201

@app.route("/api/posts/<int:post_id>/")
def get_post(post_id):
  """
  Get post by post_id
  """
  post = posts.get(post_id)
  if not post:
    return json.dumps({"error": "Post not found"}), 404
  return json.dumps(post), 200

@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
  """
  Delete post by post_id
  """
  post = posts.get(post_id)
  if not post:
    return json.dumps({"error": "Post not found"}), 404

  del posts[post_id]
  if post_id in comments:
    del comments[post_id]
  return json.dumps(post), 200

@app.route("/api/posts/<int:post_id>/comments/")
def get_comment(post_id):
  """
  Retrieve all comments of post with post_id
  """
  post = posts.get(post_id)
  if not post:
    return json.dumps({"error": "Post not found"}), 404
  if not post_id in comments:
    return json.dumps({"error": "Comment not found"}), 404

  res = {"comments": list(comments[post_id].values())}
  return json.dumps(res), 200
  
@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
  """
  Create a comment for post with post_id
  """
  post = posts.get(post_id)
  if not post:
    return json.dumps({"error": "Post not found"}), 404

  global comment_id_counter
  body = json.loads(request.data)
  comment = {
    "id": comment_id_counter,
    "upvotes": 1,
    "text": body["text"],
    "username": body["username"]
  }  
  if not post_id in comments:
    comments[post_id] = {}
  comments[post_id][comment_id_counter] = comment
  comment_id_counter += 1
  return json.dumps(comment), 201

@app.route("/api/extra/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment_extra(post_id):
  """
  Create a comment for post with post_id
  """
  post = posts.get(post_id)
  if not post:
    return json.dumps({"error": "Post not found"}), 404

  global comment_id_counter
  body = json.loads(request.data)
  if (false_input(body["text"]) or false_input(body["username"])):
    return json.dumps({"error": "Invalid request"}), 401
  comment = {
    "id": comment_id_counter,
    "upvotes": 1,
    "text": body["text"],
    "username": body["username"]
  }  
  if not post_id in comments:
    comments[post_id] = {}
  comments[post_id][comment_id_counter] = comment
  comment_id_counter += 1
  return json.dumps(comment), 201

@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"])
def update_comment(post_id, comment_id):
  """
  Update comment with comment_id
  """
  post = posts.get(post_id)
  if not post:
    return json.dumps({"error": "Post not found"}), 404
  if not post_id in comments:
    return json.dumps({"error": "Comment not found"}), 404
  comment = comments[post_id].get(comment_id)
  if not comment:
    return json.dumps({"error": "Comment not found"}), 404

  body = json.loads(request.data)
  comment["text"] = body["text"]
  return json.dumps(comment), 200

@app.route("/api/extra/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"])
def update_comment_extra(post_id, comment_id):
  """
  Update comment with comment_id
  """
  post = posts.get(post_id)
  if not post:
    return json.dumps({"error": "Post not found"}), 404
  if not post_id in comments:
    return json.dumps({"error": "Comment not found"}), 404
  comment = comments[post_id].get(comment_id)
  if not comment:
    return json.dumps({"error": "Comment not found"}), 404

  body = json.loads(request.data)
  if (false_input(body["text"])):
    return json.dumps({"error": "Invalid request"}), 401
  comment["text"] = body["text"]
  return json.dumps(comment), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
