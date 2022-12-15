from flask import Flask
from dotenv import load_dotenv
from config import BaseConfig
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
load_dotenv()
app.config.from_object(BaseConfig)
db.init_app(app)


from hubble_reports import views


if __name__ == "__main__":
    app.run()
