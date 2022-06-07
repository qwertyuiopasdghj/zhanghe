from aiohttp import web
from serv.database import CourseGrade, DbExecutor, Course, Student
from serv.log import logger
from serv.config import web_routes
from serv.jinjapage import get_location, jinjapage


@web_routes.post("/action/course/add")
async def action_student_add(request):
    params = await request.post()
    no = params.get("no")
    name = params.get("name")
    semester = params.get("semester")
    class_hours = params.get("class_hours")
    credit = params.get("credit")
    sub_class = params.get("sub_class")
    capacity = params.get("capacity")
    teacher = params.get("teacher")
    time = params.get("time")
    location = params.get("location")
    course = Course(
        no=no, name=name, credit=credit, semester=semester, class_hours=class_hours,
        sub_class=sub_class, capacity=capacity,
        time=time, location=location, teacher=teacher
    )
    logger.info(f"Adding course: {course}")
    db = request.app["db"]
    db.insert(course)

    return web.HTTPFound(location="/course")


@web_routes.post("/action/course/search")
async def action_student_search(request):
    params = await request.post()
    name = params.get("name")
    logger.info(f"Search for name = {name}")
    if not name:
        return web.HTTPBadRequest(text="name=`{name}` invalid")
    db: DbExecutor = request.app["db"]
    courses = db.session.query(Course).filter(Course.name.like(f"%{name}%")).all()
    courses = sorted(courses, key=lambda course: (course.no, course.sub_class))
    logger.info(f"Found course length: {len(courses)}")

    return jinjapage(
        'course_list.html',
        location=get_location(request),
        courses=courses,
        add_course=0,
    )


@web_routes.post("/action/course/edit/{cou_sn}")
async def edit_course_action(request):
    cou_sn = request.match_info.get("cou_sn")
    if cou_sn is None:
        return web.HTTPBadRequest(text="cou_sn must be required")

    params = await request.post()
    name = params.get("name")
    no = params.get("no")
    semester = params.get("semester")
    class_hours = params.get("class_hours")
    credit = params.get("credit")
    sub_class = params.get("sub_class")
    capacity = params.get("capacity")
    teacher = params.get("teacher")
    time = params.get("time")
    location = params.get("location")

    try:
        cou_sn = int(cou_sn)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    db: DbExecutor = request.app["db"]
    db.update(
        Course, {"sn":cou_sn},
        {
            "name": name,
            "no": no,
            "semester": semester,
            "class_hours": class_hours,
            "credit": credit,
            "sub_class": sub_class,
            "capacity": capacity,
            "teacher": teacher,
            "location": location,
            "time": time,
        }
    )

    return web.HTTPFound(location="/course")


@web_routes.post("/action/course/delete/{cou_sn}")
async def delete_course_action(request):
    cou_sn = request.match_info.get("cou_sn")
    logger.info(f"Delete user: {cou_sn}")
    if cou_sn is None:
        return web.HTTPBadRequest(text="cou_sn must be required")

    db: DbExecutor = request.app["db"]
    db.delete(CourseGrade, cou_sn=cou_sn)
    db.delete(Course, sn=cou_sn)

    return web.HTTPFound(location="/course")

@web_routes.post("/action/course/selection")
async def select_course_action(request):
    db: DbExecutor = request.app["db"]
    request_query = request.rel_url.query
    params = await request.post()
    stu_no = params.get("stu_no")
    if not stu_no:
        return web.HTTPBadRequest(text=f"{stu_no} invalid")
    student = db.query(Student, no=stu_no)
    if not student:
        return web.HTTPBadRequest(text=f"{stu_no} invalid")
    stu_sn = student[0].sn
    if "cou_sn" in request_query:
        course_sn = request_query.getall("cou_sn")
    else:
        return web.HTTPBadRequest(text="cou_sn must be provided as queries")
    courses = db.session.query(Course).filter(Course.sn.in_(course_sn))
    for course in courses:
        if course.selected >= course.capacity:
            return web.HTTPBadRequest(text=f"{course.name} full")
        content = db.query(CourseGrade, stu_sn=stu_sn, cou_sn=course.sn)
        if not content:
            course.selected += 1
            course_grade = CourseGrade(stu_sn=stu_sn, cou_sn=course.sn, grade=-1)
            db.insert(course_grade)
        else:
            logger.info(f"Already selected for {course.name} for {student[0].name}")
    db.session.commit()
    # Create course grade pair

    # Increase selected

    return web.HTTPFound(location="/course")
