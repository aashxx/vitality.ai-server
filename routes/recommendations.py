import datetime
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.generativeai as genai
from config import Config

recommendation_bp = Blueprint('recommendation', __name__)

genai.configure(api_key=Config.GEMINI_API_KEY)  
model_gemini = genai.GenerativeModel("gemini-1.5-flash")

def generate_prompt(risk_level, vitals, cardio_risk, hyper_risk):
    
    if risk_level == "low":
        return (
            f"The patient is healthy. Their current vitals are {vitals}. Provide general wellness tips "
            f"like diet, exercise, and lifestyle improvements to maintain good health. Please ignore bold characters in your response and keep it plain."
        )

    prompt = (
        f"Patient Status: High Risk\n"
        f"Vitals: {vitals}\n"
    )

    if cardio_risk:
        prompt += "The patient has a high risk of cardiovascular disease. Provide dietary and lifestyle recommendations to reduce this risk. Please ignore bold characters in your response and keep it plain.\n"

    if hyper_risk:
        prompt += "The patient has a high risk of hypertension. Provide advice on lowering blood pressure through diet and exercise. Please ignore bold characters in your response and keep it plain.\n"

    prompt += "Generate a personalized health recommendation to improve the patient's condition. Please ignore bold characters in your response and keep it plain."

    return prompt

def get_ai_recommendation(prompt):
    try:
        response = model_gemini.generate_content(prompt)
        return response.text if response else "No recommendation available."
    except Exception as e:
        return f"Error: {str(e)}"

@recommendation_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_recommendation():
    current_user = get_jwt_identity() 

    patient = current_app.mongo.db.users.find_one({"email": current_user})
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    if patient["riskLevel"] == "low":
        return jsonify({"message": "Patient is healthy, no recommendation needed."}), 200

    vitals = {
        "heartRate": patient["heartRate"],
        "sysBP": patient["sysBP"],
        "diaBP": patient["diaBP"],
        "BMI": patient["BMI"],
        "bodyTemp": patient["bodyTemp"]
    }
    
    prompt = generate_prompt(
        patient["riskLevel"], 
        vitals, 
        patient["cardiovascularRisk"], 
        patient["hypertensionRisk"]
    )
    
    recommendation_text = get_ai_recommendation(prompt)

    record = {
        "patientEmail": current_user,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": patient["riskLevel"],
        "recommendation": recommendation_text,
    }

    current_app.mongo.db.recommendations.insert_one(record)

    return jsonify({
        "message": "Health recommendation generated successfully.",
        "recommendation": recommendation_text
    }), 200
