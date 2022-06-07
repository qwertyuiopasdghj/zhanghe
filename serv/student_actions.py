from aiohttp import web
from serv.database import CourseGrade, DbExecutor, Student, Course, CourseGrade
from serv.jinjapage import get_location, jinjapage
from serv.log import logger
from serv.config import web_routes


@web_routes.post("/action/student/add")
async def action_student_add(request):
    params = await request.post()
    no = params.get("no")
    name = params.get("name")
    gender = params.get("gender")
    school = params.get("school")
    year = params.get("year")
    clazz = params.get("clazz")
    student = Student(no=no, name=name, gender=gender, school=school, year=year, clazz=clazz)
    logger.info(f"Adding student: {student}")
    db = request.app["db"]
    db.insert(student)

    return web.HTTPFound(location="/student")


@web_routes.post("/action/student/edit/{stu_sn}")
async def edit_student_action(request):
    stu_sn = request.match_info.get("stu_sn")
    if stu_sn is None:
        return web.HTTPBadRequest(text="stu_sn must be required")

    params = await request.post()
    update = {
        "no" : params.get("no"),
        "name" : params.get("name"),
        "gender" : params.get("gender"),
        "school" : params.get("school"),
        "year" : params.get("year"),
        "clazz" : params.get("clazz"),
    }

    try:
        stu_sn = int(stu_sn)
    except ValueError:
        return web.HTTPBadRequest(text=f"invalid value for {stu_sn}")

    db: DbExecutor = request.app["db"]
    db.update(Student, {"sn":stu_sn}, update)

    return web.HTTPFound(location="/student")


@web_routes.post("/action/student/delete/{stu_sn}")
async def delete_student_action(request):
    stu_sn = request.match_info.get("stu_sn")
    logger.info(f"Delete user: {stu_sn}")
    if stu_sn is None:
        return web.HTTPBadRequest(text="stu_sn must be required")

    db: DbExecutor = request.app["db"]
    db.delete(CourseGrade, stu_sn=stu_sn)
    db.delete(Student, sn=stu_sn)

    return web.HTTPFound(location="/student")

@web_routes.post("/action/student/search")
async def action_student_search(request):
    params = await request.post()
    no = params.get("stu_no")
    cou_sn = params.get("cou_sn")
    cou_semester = params.get("cou_semester")
    db:DbExecutor = request.app["db"]
    if no:
        students = db.query(Student, no=no)
        student = students[0]
        logger.info(f"Search courses for: stu_sn = {student.sn}, cou_sn= {cou_sn}")
    else:
        student = None
        logger.info(f"Search courses for: users, cou_sn= {cou_sn}")
    query = db.session.query(
        Student, Course, CourseGrade
    )
    if no:
        query = query.filter(Student.no==no)
    filter_course_kwargs = {}
    if cou_sn:
        filter_course_kwargs["sn"] = cou_sn
    if cou_semester:
        filter_course_kwargs["semester"] = cou_semester
    if filter_course_kwargs:
        query = query.join(Course).filter_by(**filter_course_kwargs)
    else:
        query = query.join(Course)
    result = query.all()
    logger.info(f"Find courses length = {len(result)}, {result}")
    return jinjapage(
        'student_search.html',
        location=get_location(request),
        student=student,
        courses=result,
    )
