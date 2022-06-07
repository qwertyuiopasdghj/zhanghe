from serv.config import web_routes
from serv.jinjapage import jinjapage, get_location


@web_routes.get('/error')
async def dialog_error(request):
    message = request.query.get("message")
    return_path = request.query.get("return")

    return jinjapage('dialog_error.html',
                     message=message,
                     location=get_location(request),
                     return_path=return_path)
