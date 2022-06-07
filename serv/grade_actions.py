from aiohttp import web
from urllib.parse import urlencode
from psycopg.errors import UniqueViolation, ForeignKeyViolation
from sqlalchemy.exc import IntegrityError

from serv.database import CourseGrade, DbExecutor
from serv.log import logger
from serv.config import web_routes

@web_routes.post('/action/grade/add')
async def action_grade_add(request):
    params = await request.post()
    stu_sn = params.get("stu_sn")
    cou_sn = params.get("cou_sn")
    grade = params.get("grade")

    if stu_sn is None or cou_sn is None or grade is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, grade must be required")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        grade = float(grade)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    db:DbExecutor = request.app["db"]
    result = db.query(CourseGrade, stu_sn=stu_sn, cou_sn=cou_sn)
    if result:
        logger.info(f"Found course information")
        result[0].grade = grade
        db.session.commit()
    else:
        try:
            db.insert(CourseGrade(stu_sn=stu_sn, cou_sn=cou_sn, grade=grade))
        except (IntegrityError, UniqueViolation):
            logger.info(f"IntegrityError for {stu_sn} {cou_sn}")
            query = urlencode({
                "message": "已经添加该学生的课程成绩",
                "return": "/grade"
            })
            return web.HTTPFound(location=f"/error?{query}")
        except ForeignKeyViolation as ex:
            return web.HTTPBadRequest(text=f"无此学生或课程: {ex}")

    return web.HTTPFound(location="/grade")


@web_routes.post('/action/grade/edit/{stu_sn}/{cou_sn}')
async def edit_grade_action(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    params = await request.post()
    grade = params.get("grade")

    try:
        stu_sn = int(stu_sn)
        cou_sn = int(cou_sn)
        grade = float(grade)
    except ValueError:
        return web.HTTPBadRequest(text="invalid value")

    db: DbExecutor = request.app["db"]
    db.update(CourseGrade, {"stu_sn":stu_sn, "cou_sn":cou_sn}, {"grade":grade})

    return web.HTTPFound(location="/grade")


@web_routes.post('/action/grade/delete/{stu_sn}/{cou_sn}')
async def delete_grade_action(request):
    stu_sn = request.match_info.get("stu_sn")
    cou_sn = request.match_info.get("cou_sn")
    logger.info(f"Delete student: {stu_sn}, course: {cou_sn}")
    if stu_sn is None or cou_sn is None:
        return web.HTTPBadRequest(text="stu_sn, cou_sn, must be required")

    db: DbExecutor = request.app["db"]
    db.delete(CourseGrade, stu_sn=stu_sn, cou_sn=cou_sn)

    return web.HTTPFound(location="/grade")
