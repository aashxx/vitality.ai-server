import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import numpy as np
import joblib
from tensorflow import keras

prediction_bp = Blueprint('prediction', __name__)

deep_ann_model = keras.models.load_model('ml_models/deep_ann_model.keras')
mlp_model = joblib.load('ml_models/mlp_model.pkl')
rf_model = joblib.load('ml_models/random_forest_model.pkl')
scaler = joblib.load('ml_models/scaler.pkl')

def preprocess_input(data):
    input_data = np.array([[data["age"], data["sysBP"], data["diaBP"], data["BMI"], data["heartRate"], data["bodyTemp"]]])
    return scaler.transform(input_data)

@prediction_bp.route('/risk', methods=['POST'])
def predict_risk():
    data = request.json
    input_data = preprocess_input(data)
    prediction = deep_ann_model(input_data)
    risk_level = 'high' if prediction[0][0] < 0.5 else 'low'

    record = {
        'patientEmail': data['email'],
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'vitals': {
            "heartRate": data["heartRate"],
            "sysBP": data["sysBP"],
            "diaBP": data["diaBP"],
            "BMI": data["BMI"],
            "bodyTemp": data["bodyTemp"]
        },
        "riskLevel": risk_level
    }

    current_app.mongo.db.vitals_history.insert_one(record)

    return jsonify({
        'message': 'Vitals recorded successfully',
        'risk': risk_level
    }), 200
