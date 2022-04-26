from email.quoprimime import body_check
import json

from db import db, Course, User, Assignment
from flask import Flask, request

db_filename = "cms.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# your routes here
@app.route("/api/courses/")
def get_courses():
    """
    Endpoint for getting all courses
    """
    return success_response({
        "courses": [c.serialize() for c in Course.query.all()]
    })


@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    body = json.loads(request.data)
    code = body.get("code", -1)
    name = body.get("name", -1)
    if code == -1 or name == -1:
        return failure_response("Missing request information", 400)

    new_course = Course(code=code, name=name)
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/")
def get_course_by_id(course_id):
    """
    Endpoint for getting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint for deleting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")

    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    name = body.get("name", -1)
    netid = body.get("netid", -1)
    if name == -1 or netid == -1:
        return failure_response("Missing request information", 400)

    new_user = User(name=name, netid=netid)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
    """
    Endpoint for getting a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())


@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    """
    Endpoint for adding user to course with course_id
    """
    body = json.loads(request.data)
    user_id = body.get("user_id", -1)
    type = body.get("type", -1)
    if user_id == -1 or type == -1:
        return failure_response("Missing request information", 400)
    
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    
    if type == "instructor":
        if user not in course.instructors:
            course.instructors.append(user)
    else:
        if user not in course.students:
            course.students.append(user)

    db.session.commit()
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/drop/", methods=["POST"])
def drop_student_from_course(course_id):
    """
    Endpoint for dropping student from a course with course_id
    """
    body = json.loads(request.data)
    user_id = body.get("user_id", -1)
    if user_id == -1:
        return failure_response("Missing request information")

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")

    if user not in course.students:
        return failure_response("user has not been added to this course")
    
    course.students.remove(user)
    db.session.commit()
    return success_response(user.serialize())

    

@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Endpoint for creating an assignment
    """
    body = json.loads(request.data)
    title = body.get("title", -1)
    due_date = body.get("due_date", -1)
    if title == -1 or due_date == -1:
        return failure_response("Missing request information", 400)

    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")

    new_assignment = Assignment(title=title, due_date=due_date, course_id=course_id)
    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(), 201)


@app.route("/api/assignments/<int:assignment_id>/", methods=["POST"])
def update_assignment(assignment_id):
    """
    Endpoint for updating an assignment
    """
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        return failure_response("Assignment not found")

    body = json.loads(request.data)
    assignment.title = body.get("title", assignment.title)
    assignment.due_date = body.get("due_date", assignment.due_date)

    db.session.commit()
    return success_response(assignment.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
