from flask import Flask
from application.database import db
 
app = None

def create_app():
    app = Flask(__name__) 
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///ecard.sqlite3"
    app.config["SECRET_KEY"] = "some-very-secret-random-string"
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
from application.controllers import * 
from application.resources import *



if __name__ == "__main__":
    app.run()