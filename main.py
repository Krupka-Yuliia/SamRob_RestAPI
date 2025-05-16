from flask import Flask

from models import db
from views import library

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://admin:PassWord@db:3306/books11"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
    app.register_blueprint(library, url_prefix="/v1/api")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
