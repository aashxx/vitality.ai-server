import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np
import joblib
from tensorflow import keras

prediction_bp = Blueprint('prediction', __name__)

deep_ann_model = keras.models.load_model('ml_models/deep_ann_model.keras')
mlp_model = joblib.load('ml_models/mlp_model.pkl')
rf_model = joblib.load('ml_models/random_forest_model.pkl')
scaler = joblib.load('ml_models/scaler.pkl')

def preprocess_input(data):
    try:
        BMI = data['weight'] / (data['height'] ** 2) if data['height'] > 0 else 0 
        input_data = np.array([[data["age"], data["sysBP"], data["diaBP"], BMI, data["heartRate"], data["bodyTemp"]]])  
        return scaler.transform(input_data), BMI  
    except KeyError as e:
        return None, f"Missing field: {str(e)}"

def check_hypertension(model, age, BPmeds, sysBP, diaBP, BMI, heartRate):
    input_data = np.array([[age, BPmeds, sysBP, diaBP, BMI, heartRate]])
    return bool(model.predict(input_data)[0])

def check_cardiovascular(model, age, weight, sysBP, diaBP, BMI):
    input_data = np.array([[age, weight, sysBP, diaBP, BMI]])
    return bool(model.predict(input_data)[0])

@prediction_bp.route('/risk', methods=['POST'])
@jwt_required()
def predict_risk():
    current_user = get_jwt_identity()
    data = request.json

    patient = current_app.mongo.db.users.find_one({"email": current_user})
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    input_data, BMI = preprocess_input(data)
    if input_data is None:
        return jsonify({"error": BMI}), 400 

    deep_prediction = deep_ann_model.predict(input_data)[0][0]
    risk_level = "high" if deep_prediction > 0.5 else "low"

    has_hypertension = False
    has_cardiovascular = False

    if risk_level == "high":
        has_hypertension = check_hypertension(rf_model, data["age"], data["BPmeds"], data["sysBP"], data["diaBP"], BMI, data["heartRate"])
        has_cardiovascular = check_cardiovascular(mlp_model, data["age"], data["weight"], data["sysBP"], data["diaBP"], BMI)

    record = {
        "patientEmail": current_user,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "vitals": {
            "heartRate": data["heartRate"],
            "sysBP": data["sysBP"],
            "diaBP": data["diaBP"],
            "BMI": BMI,  
            "bodyTemp": data["bodyTemp"]
        },
        "riskLevel": risk_level,
        "cardiovascularRisk": has_cardiovascular,
        "hypertensionRisk": has_hypertension
    }

    current_app.mongo.db.vitals_history.insert_one(record)
    current_app.mongo.db.users.update_one(
        {"email": current_user}, 
        {"$set": {
            "heartRate": data["heartRate"],
            "sysBP": data["sysBP"],
            "diaBP": data["diaBP"],
            "BMI": BMI,
            "bodyTemp": data["bodyTemp"],
            "riskLevel": risk_level,
            "cardiovascularRisk": has_cardiovascular,
            "hypertensionRisk": has_hypertension,
            "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }}
    )

    return jsonify({
        "message": "Vitals recorded successfully",
        "risk": risk_level,
        "cardiovascularRisk": has_cardiovascular,
        "hypertensionRisk": has_hypertension
    }), 200