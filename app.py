from flask import Flask, render_template
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

@app.errorhandler(404)
def page_not_found(e):
    context = {
        'status_title': 'Not Found',
        'status_code': 404,
        'status_message': 'Page not found',
    }
    return render_template('custom_error_page.html', context=context), 404


if __name__ == "__main__":
    app.run()
