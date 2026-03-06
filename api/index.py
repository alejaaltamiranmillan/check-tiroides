from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
import numpy as np

app = Flask(__name__)
CORS(app)

# Configuración de rutas para archivos en Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'modelo_tiroides.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')

# Cargar el cerebro de la IA
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ Recursos cargados correctamente")
except Exception as e:
    print(f"❌ Error de carga: {str(e)}")

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Array con los 5 parámetros del dataset new-thyroid
        input_data = np.array([[
            float(data['t3_resin']),
            float(data['t4_total']),
            float(data['t3_total']),
            float(data['tsh']),
            float(data['t4_diff'])
        ]])
        
        # Escalar y predecir
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]
        
        # Mapeo según el dataset original (1: Normal, 2: Hiper, 3: Hipo)
        mapping = {1: "Normal", 2: "Hipertiroidismo", 3: "Hipotiroidismo"}
        resultado = mapping.get(int(prediction), "Desconocido")
        
        return jsonify({'status': 'success', 'diagnostico': resultado})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400