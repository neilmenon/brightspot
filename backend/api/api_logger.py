from flask import current_app

def log(message, app=None):
    if app:
        app.logger.debug(message)
    else:
        current_app.logger.debug(message)