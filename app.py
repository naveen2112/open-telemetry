from flask import Flask
from dotenv import load_dotenv
from config import BaseConfig
from flask_session import Session
from flask_login import LoginManager, login_required

from hubble_reports.models import db


app = Flask(
    __name__,
    template_folder="hubble_reports/templates",
    static_folder="hubble_reports/static",
)
app.app_context().push()
load_dotenv()
app.config.from_object(BaseConfig)
Session(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "reports.login"


from hubble_reports.hubble_reports import reports
from hubble_reports.views.error import error_page

app.register_blueprint(reports)

error_code_list = [401, 403, 404, 405, 500]
for error_code in error_code_list:
    app.register_error_handler(error_code, error_page)


from hubble_reports.views.dash import dash_app

for view_func in app.view_functions:
    if not (view_func.startswith("reports")) and view_func.startswith(
        dash_app.config["routes_pathname_prefix"]
    ):
        app.view_functions[view_func] = login_required(app.view_functions[view_func])

if __name__ == "__main__":
    app.run()
