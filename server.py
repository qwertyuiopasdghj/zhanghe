from aiohttp import web


from serv.config import web_routes, home_path

import serv.error_views
import serv.main_views
import serv.grade_views
import serv.grade_actions
import serv.student_views
import serv.student_actions
import serv.course_views
import serv.course_actions

from serv import database

app = web.Application()

db = database.initialize(host="localhost", port=5432, user="examdb", password="pass", db_name="examdb")
app["db"] = db


app.add_routes(web_routes)
app.add_routes([web.static("/", home_path / "static")])
# serv.dblock.setup(app, dsn="host=localhost dbname=examdb user=examdb")

if __name__ == "__main__":
    web.run_app(app, port=8080, access_log=None)
