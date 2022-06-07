from aiohttp import web
from serv.config import web_routes
from serv.log import logger


@web_routes.get("/")
async def home_page(request):
    _ = request
    page = "/grade"
    logger.info(f"Default move to page {page}")
    return web.HTTPFound(location=page)

