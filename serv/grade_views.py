from aiohttp import web
from serv.config import web_routes
from serv.jinjapage import jinjapage, get_location
from serv.database import Student, Course, CourseGrade
from serv.log import logger


@web_routes.get("/grade")
async def grades_home_page(request):
    db = request.app["db"]
    # All students
    students = db.query(Student)

    # All courses
    courses = db.query(Course)

    # Join
    items = db.session.query(
        Student, Course, CourseGrade
    ).filter(
        Student.sn == CourseGrade.stu_sn,
    ).filter(
        Course.sn == CourseGrade.cou_sn,
    ).order_by(Student.sn, Course.sn).all()
    return jinjapage(
        "grade_list.html",
        location=get_location(request),
        students=students,
        courses=courses,
        items=items
    )


@web_routes.get("/grade/edit/{stu_sn}/{cou_sn}")
async def grade_editor_page(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    db = request.app["db"]
    result = db.query(
        CourseGrade, **{"stu_sn":stu_sn, "cou_sn":cou_sn}
    )

    if not result:
        return web.HTTPNotFound(text=f"no such grade: stu_sn={stu_sn}, cou_sn={cou_sn}")

    return jinjapage("grade_edit.html",
                     location=get_location(request),
                     stu_sn=stu_sn,
                     cou_sn=cou_sn,
                     grade=result[0].grade)


@web_routes.get("/grade/delete/{stu_sn}/{cou_sn}")
async def grade_deletion_page(request: web.Request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    db = request.app["db"]
    result = db.session.query(
        CourseGrade, Student, Course
    ).filter_by(
        stu_sn=stu_sn, cou_sn=cou_sn
    ).join(Student).join(Course).all()
    logger.info(f"Result size: {len(result)}")
    for item in result:
        logger.info(item)

    if not result:
        return web.Response(
            text=f"no such grade: stu_sn={stu_sn}, cou_sn={cou_sn}",
            status=404,
            content_type="text/html"
        )

    return jinjapage(
        "grade_dialog_deletion.html",
        location=get_location(request),
        record=result[0]
    )
