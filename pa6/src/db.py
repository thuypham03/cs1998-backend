from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

instructors_association_table = db.Table(
    "instructors_association",
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
)

students_association_table = db.Table(
    "students_association",
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
)

# your classes here
class Course(db.Model):
    """
    Course model

    Has a many-to-many relationship with the User model
    Has a one-to-many relationship with the Assignment model
    Has a one-to-many relationship with the Submission model
    """
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship("Assignment", cascade="delete")
    instructors = db.relationship("User", secondary=instructors_association_table, back_populates="instructor_courses")
    students = db.relationship("User", secondary=students_association_table, back_populates="student_courses")

    def __init__(self, **kwargs):
        """
        Initialize Course object
        """
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")

    def serialize(self):
        """
        Serialize Course object
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.simple_serialize() for a in self.assignments],
            "instructors": [i.simple_serialize() for i in self.instructors],
            "students": [s.simple_serialize() for s in self.students]
        }

    def simple_serialize(self):
        """
        Simple_erialize Course object
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
        }

class User(db.Model):
    """
    User model

    Has a many-to-many relationship with the Course model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    instructor_courses = db.relationship("Course", secondary=instructors_association_table, back_populates="instructors")
    student_courses = db.relationship("Course", secondary=students_association_table, back_populates="students")

    def __init__(self, **kwargs):
        """
        Initialize User object
        """
        self.name = kwargs.get("name")
        self.netid = kwargs.get("netid")
    
    def _getCourse(self):
        courses = self.instructor_courses[:]
        for cur in self.student_courses:
            if cur not in courses:
                courses.append(cur)
        return [c.simple_serialize() for c in courses]

    def serialize(self):
        """
        Serialize User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": self._getCourse()
        }

    def simple_serialize(self):
        """
        Simple_serialize User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }

    def hasCourse(self, course_id):
        course = Course.query.filter_by(id=course_id).first()
        return course in self.student_courses

class Assignment(db.Model):
    """
    Assignment model

    Has a one-to-many relationship with the Submission model
    """
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize Assignment object
        """
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")
        self.course_id = kwargs.get("course_id")
    
    def _getCourse(self):
        course = Course.query.filter_by(id=self.course_id).first()
        return course.simple_serialize()

    def serialize(self):
        """
        Serialize Assignment object
        """
        return {
            "id" : self.id,
            "title": self.title,
            "due_date": self.due_date,
            "course" : self._getCourse()
        }

    def simple_serialize(self):
        """
        Simple_serialize Assignment object
        """
        return {
            "id" : self.id,
            "title": self.title,
            "due_date": self.due_date
        }


class Submission(db.Model):
    """
    Submission model
    """
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False)

    def __init__(self, content, user_id, assignment_id, score=None):
        """
        Initialize Submission object
        """
        self.content = content
        self.user_id = user_id
        self.assignment_id = assignment_id
        self.score = score

    def serialize(self):
        """
        Serialize Submission object
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "assignment_id": self.assignment_id,
            "score": self.score
        }
