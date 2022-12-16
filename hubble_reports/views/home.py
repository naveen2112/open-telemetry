from app import app


@app.route("/")
def hello_world():
    return "<p>Hello World, Welcome to Home Page!</p>"
