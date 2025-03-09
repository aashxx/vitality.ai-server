# 🏥 Vitality AI - Flask Backend

Vitality AI is an AI-powered health monitoring system that predicts health risks, provides AI-driven care recommendations, and stores patient vitals securely. This backend is built using **Flask, MongoDB, and TensorFlow, and connects with a React Native Expo frontend.

## 🛠️ Installation & Setup

### 1️⃣ **Clone the Repository**
```sh
git clone https://github.com/your-username/vitality-ai-backend.git
cd vitality-ai-backend
```

### 2️⃣ **Create a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3️⃣ **Install Dependencies**
```sh
pip install -r requirements.txt
```

### 4️⃣ **Set Up MongoDB Atlas**
1. Create a **free MongoDB Atlas cluster**
2. Get the **connection URI** and update `config.py`:
   ```python
   MONGO_URI = "mongodb+srv://your-username:your-password@your-cluster.mongodb.net/main-db?retryWrites=true&w=majority"
   ```
3. **Whitelist IPs** in MongoDB Atlas:
   ```
   3.9.0.0/16
   35.176.0.0/16
   52.56.0.0/16
   ```

### 5️⃣ **Run the Flask Server**
```sh
python server.py
```
Your server will now run at:  
🔗 **http://127.0.0.1:5000**

---

## 🔥 API Endpoints

### **1️⃣ Authentication Endpoints** (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register a new patient |
| `POST` | `/api/auth/login` | Login and get JWT token |
| `GET` | `/api/auth/profile` | Get user profile (JWT required) |

---

### **2️⃣ Health Risk Prediction** (`/api/predict`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict/risk` | Predict if the patient is at high risk |

**🔹 Example Request (Body):**
```json
{
  "email": "user@example.com",
  "age": 45,
  "sysBP": 140,
  "diaBP": 90,
  "BMI": 29.5,
  "heartRate": 80,
  "bodyTemp": 98.6
}
```

**🔹 Example Response:**
```json
{
  "message": "Vitals recorded successfully",
  "risk": "high"
}
```

---

### **3️⃣ AI Health Recommendations** (`/api/recommendations`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/recommendation/generate` | Generate AI-based health tips |

---

### **4️⃣ Alerts & Notifications** (`/api/alerts`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/alert/trigger` | Send an alert if a patient is at high risk |


