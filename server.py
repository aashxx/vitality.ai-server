from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models.db import init_db

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
jwt = JWTManager(app)
mongo = init_db(app)

from routes.auth import auth_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")

if __name__ == "__main__":
    app.run(debug=True)
