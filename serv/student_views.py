from aiohttp import web
from serv.config import web_routes
from serv.jinjapage import get_location, jinjapage
from serv.database import DbExecutor, Student, Course
from serv.log import logger


@web_routes.get("/student")
async def view_student_list(request):
    db:DbExecutor = request.app["db"]
    students = db.query(Student)
    courses = db.query(Course)
    semesters = sorted(list(set([c.semester for c in courses])))
    return jinjapage(
        'student_list.html',
        location=get_location(request),
        students=students,
        courses=courses,
        semesters=semesters,
    )


@web_routes.get("/student/edit/{stu_sn}")
async def student_editor_page(request):
    stu_sn = request.match_info.get("stu_sn")
    if stu_sn is None:
        return web.HTTPBadRequest(text="stu_sn, must be required")

    db = request.app["db"]
    result = db.query(
        Student, **{"sn":stu_sn}
    )

    if not result:
        return web.HTTPNotFound(text=f"no such grade: stu_sn={stu_sn}")
    logger.info(f"Editing: {result[0]}")

    return jinjapage(
        "student_edit.html",
        location=get_location(request),
        stu_sn=stu_sn,
        student=result[0],
    )


@web_routes.get("/student/delete/{stu_sn}")
async def student_deletion_page(request: web.Request):
    stu_sn = request.match_info.get("stu_sn")
    db = request.app["db"]
    result = db.session.query(
        Student
    ).filter_by(
        sn=stu_sn
    ).one_or_none()

    if not result:
        return web.Response(
            text=f"no such student: stu_sn={stu_sn}",
            status=404,
            content_type="text/html"
        )

    return jinjapage(
        "student_dialog_deletion.html",
        location=get_location(request),
        record=result
    )
