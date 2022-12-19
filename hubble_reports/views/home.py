from hubble_reports.hubble_reports import reports


@reports.route("/")
def hello_world():
    return "<p>Hello World, Welcome to Home Page!</p>"
