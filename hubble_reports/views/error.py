from flask import render_template


def error_page(e):
    context = {
        401: {
            "status_title": "Unauthorized",
            "status_code": 401,
            "status_message": "This user has no permission to use this route",
        },
        403: {
            "status_title": "Forbidden",
            "status_code": 403,
            "status_message": "Permission required to use this route",
        },
        404: {
            "status_title": "Not Found",
            "status_code": 404,
            "status_message": "Page not found",
        },
        405: {
            "status_title": "Method Not Allowed",
            "status_code": 405,
            "status_message": "Route does not support this method",
        },
        500: {
            "status_title": "Internal Server Error",
            "status_code": 500,
            "status_message": "Something wrong in sever",
        },
    }
    return render_template("custom_error_page.html", context=context[e.code]), e.code
