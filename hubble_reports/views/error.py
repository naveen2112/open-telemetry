import logging
from flask import Flask, render_template
from hubble_reports.utils import get_logger

logger = get_logger(__name__,level=logging.DEBUG)

def error_page(e):
    logger.info(f"\n\n\nError code is {e}\n")
    context = {
        403:
        {
            'status_title': 'Forbidden',
            'status_code': 403,
            'status_message': 'Permission required to use this route',
        },
        404:
        {
            'status_title': 'Not Found',
            'status_code': 404,
            'status_message': 'Page not found',
        },
        405:
        {
            'status_title': 'Method Not Allowed',
            'status_code': 405,
            'status_message': 'Route does not support this method',
        },
        500:
        {
            'status_title': 'Internal Server Error',
            'status_code': 500,
            'status_message': 'Something wrong in sever',
        },
    }
    return render_template('custom_error_page.html', context=context[e.code]), e.code