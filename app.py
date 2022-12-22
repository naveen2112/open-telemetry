from flask import Flask
from dotenv import load_dotenv
from config import BaseConfig
from hubble_reports.models import db
from hubble_reports.hubble_reports import reports
from flask_session import Session

app = Flask(__name__, static_folder='hubble_reports/static')
load_dotenv()
app.config.from_object(BaseConfig)
Session(app)
db.init_app(app)


app.register_blueprint(reports)

if __name__ == "__main__":
    app.run()
