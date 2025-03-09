import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config

alert_bp = Blueprint('alert', __name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = Config.GMAIL_CLIENT_ID 
EMAIL_PASSWORD = Config.GMAIL_APP_PASSWORD

def send_email_alert(patient_email, patient_name, emergency_contact, risk_level):
    try:
        subject = f"🚨 Emergency Alert: {patient_name}'s Health Condition is {risk_level.upper()} 🚨"
        body = (
            f"Dear Caregiver,\n\n"
            f"We wanted to inform you that {patient_name} ({patient_email}) has been detected with a **{risk_level.upper()}** health condition.\n\n"
            f"Please check on them immediately and seek medical assistance if necessary.\n\n"
            f"Best Regards,\n"
            f"Vitality AI Health Monitoring System"
        )

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = emergency_contact
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, emergency_contact, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@alert_bp.route('/trigger', methods=['POST'])
@jwt_required()
def trigger_alert():
    current_user = get_jwt_identity()  

    patient = current_app.mongo.db.users.find_one({"email": current_user})
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    if patient["riskLevel"] != "high":
        return jsonify({"message": "No alert needed. Patient is not in high risk."}), 200

    emergency_contact = patient.get("emergencyContact")
    if not emergency_contact:
        return jsonify({"error": "No emergency contact found for this patient."}), 400

    email_sent = send_email_alert(patient["email"], patient["fullName"], emergency_contact, patient["riskLevel"])

    alert_record = {
        "patientEmail": current_user,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "riskLevel": patient["riskLevel"],
        "emergencyContact": emergency_contact,
        "alertSent": email_sent
    }
    
    current_app.mongo.db.alerts.insert_one(alert_record)

    return jsonify({
        "message": "Alert triggered successfully.",
        "alertSent": email_sent
    }), 200
