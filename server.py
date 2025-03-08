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
app.mongo = mongo

from routes.auth import auth_bp
from routes.predictions import prediction_bp
from routes.recommendations import recommendation_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(prediction_bp, url_prefix="/api/predict")
app.register_blueprint(recommendation_bp, url_prefix="/api/recommendation")

if __name__ == "__main__":
    app.run(debug=True)
