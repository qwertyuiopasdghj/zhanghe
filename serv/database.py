import sqlalchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from serv.log import logger


Base = declarative_base()


class Student(Base):
    __tablename__ = "student"
    sn = Column(Integer, primary_key=True, doc="Student sequence number", autoincrement=True)
    no = Column(String(10), doc="Student number")
    name = Column(Text, doc="Student name")
    gender = Column(String(1), doc="Student gender, F/M")
    year = Column(String(10), doc="Enrolled year of student")
    school = Column(Text, doc="Student school")
    clazz = Column(Text, doc="Student class")

    # relationship
    course_grade = relationship("CourseGrade", cascade="all, delete")

    def __str__(self):
        return (
            f"Student({self.sn}, {self.no}, {self.name}, {self.gender}, "
            f"{self.year}, {self.school}, {self.clazz})"
        )


class Course(Base):
    __tablename__ = "course"
    sn = Column(Integer, primary_key=True, doc="Course sequence number", autoincrement=True)
    no = Column(String(10), doc="Course number")
    name = Column(Text, doc="Course name")
    credit = Column(Integer)
    class_hours = Column(Integer)
    semester = Column(Text, doc="semester")
    sub_class = Column(Text, doc="Subclass name")
    capacity = Column(Integer, doc="Capacity for this class", default=0)
    selected = Column(Integer, doc="Already selected", default=0)
    teacher = Column(Text, doc="teacher")
    location = Column(Text, doc="location")
    time = Column(Text, doc="class time")

    def __str__(self):
        return (
            f"Course({self.sn}, {self.no}, {self.name}, {self.credit}, "
            f"{self.class_hours}, {self.semester})"
        )


class CourseGrade(Base):
    __tablename__ = "course_grade"
    stu_sn = Column(
        Integer,
        ForeignKey("student.sn",ondelete="CASCADE"),
        doc="Student number",
        primary_key=True
    )
    cou_sn = Column(
        Integer,
        ForeignKey("course.sn", ondelete="CASCADE"),
        doc="Course number",
        primary_key=True
    )
    grade = Column(Numeric(5, 2), doc="grade for course")

    def __str__(self):
        return f"CourseGrade({self.stu_sn}, {self.cou_sn}, {self.grade})"


class DbExecutor:

    def __init__(self, host=None, port=None, db_name=None, user=None, password=None):
        logger.info(f"Initialize db: {host}:{port} on db: {db_name}")
        url = "postgresql://{}:{}@{}:{}/{}"
        url = url.format(user, password, host, port, db_name)
        engine = sqlalchemy.create_engine(url, client_encoding="utf8", echo=False)
        Session = sessionmaker(bind=engine)
        self._session = Session()
        Base.metadata.create_all(engine, checkfirst=True)

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        self._session = session

    def update(self, TableClz, filter_kwargs, update_kwargs):
        instance = self.session.query(TableClz).filter_by(**filter_kwargs).one_or_none()
        if instance is not None:
            for key, value in update_kwargs.items():
                setattr(instance, key, value)
            self.session.commit()

    def insert(self, instance):
        self.session.add(instance)
        self.session.commit()

    def delete(self, TableClz, **filter_kwargs):
        self.session.query(TableClz).filter_by(**filter_kwargs).delete()
        self.session.commit()

    def query(self, TableClz, **filter_kwargs):
        query = self.session.query(TableClz)
        if filter_kwargs:
            result = query.filter_by(**filter_kwargs).all()
        else:
            result = query.all()
        self.session.commit()
        return result



def initialize(**kwargs):
    return DbExecutor(**kwargs)
