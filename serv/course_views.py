from aiohttp import web
from serv.config import web_routes
from serv.jinjapage import get_location, jinjapage
from serv.database import DbExecutor, Course
from serv.log import logger


@web_routes.get("/course")
async def view_course_list(request):
    db:DbExecutor = request.app["db"]
    courses = db.query(Course)
    return jinjapage(
        'course_list.html',
        location=get_location(request),
        courses=courses,
    )

@web_routes.get("/course/selection")
async def view_course_selection(request):
    db:DbExecutor = request.app["db"]
    request_query = request.rel_url.query
    if "cou_sn" in request_query:
        course_sn = request.rel_url.query.getall("cou_sn")
        query = "&".join(map(lambda x: f"cou_sn={x}", course_sn))
    else:
        return web.HTTPBadRequest(text="no cou_sn in params")
    courses = db.session.query(Course).filter(Course.sn.in_(course_sn)).all()
    return jinjapage(
        'course_selection.html',
        location=get_location(request),
        courses=courses,
        query=query,
    )

@web_routes.get("/course/edit/{cou_sn}")
async def course_editor_page(request):
    cou_sn = request.match_info.get("cou_sn")
    if cou_sn is None:
        return web.HTTPBadRequest(text="cou_sn, must be required")

    db = request.app["db"]
    result = db.query(
        Course, **{"sn":cou_sn}
    )

    if not result:
        return web.HTTPNotFound(text=f"no such grade: cou_sn={cou_sn}")
    logger.info(f"Editing: {result[0]}")

    return jinjapage(
        "course_edit.html",
        location=get_location(request),
        cou_sn=cou_sn,
        course=result[0],
    )



@web_routes.get("/course/delete/{cou_sn}")
async def course_deletion_page(request: web.Request):
    cou_sn = request.match_info.get("cou_sn")
    db = request.app["db"]
    result = db.session.query(
        Course
    ).filter_by(
        sn=cou_sn
    ).one_or_none()

    if not result:
        return web.Response(
            text=f"no such course: cou_sn={cou_sn}",
            status=404,
            content_type="text/html"
        )

    return jinjapage(
        "course_dialog_deletion.html",
        location=get_location(request),
        record=result
    )
