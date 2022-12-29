from flask import Flask
from dotenv import load_dotenv
from config import BaseConfig
from flask_session import Session
from flask_login import LoginManager

from hubble_reports.models import db


app = Flask(__name__)
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

error_code_list = [403, 404, 405, 500]
for error_code in error_code_list:
    app.register_error_handler(error_code, error_page)


if __name__ == "__main__":
    app.run()
