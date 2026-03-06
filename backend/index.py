from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Obtener la ruta absoluta de los archivos .pkl
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'modelo_tiroides.pkl')
scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')

# Cargar archivos
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # El orden debe coincidir con tu entrenamiento en Colab
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
        
        # Mapeo según new-thyroid.data (1:Normal, 2:Hyper, 3:Hypo)
        mapping = {1: "Normal", 2: "Hipertiroidismo", 3: "Hipotiroidismo"}
        resultado = mapping.get(int(prediction), "Desconocido")
        
        return jsonify({'diagnostico': resultado, 'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 400

# IMPORTANTE: Vercel necesita que el objeto 'app' esté disponible.
# No incluyas app.run() aquí para producción.