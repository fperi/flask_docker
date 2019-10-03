# this is the uwsgi service that calls the flask app
from app.main import app

if __name__ == "__main__":
    app.run()
