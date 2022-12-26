import logging

from typing import Union
from functools import wraps
from flask import session, redirect

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(level)
    console = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s %(name)s] %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


def login_required(func:callable) -> callable:
 
    @wraps(func)
    def inner(*args, **kwargs) -> Union[callable, redirect]:
        if session.get('user'):
            return func(*args, **kwargs)
        else:
            return redirect('login')
    return inner