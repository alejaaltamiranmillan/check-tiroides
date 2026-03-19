#!/usr/bin/env python3
"""
Test script for Vercel decryption API
Tests all 5 cipher types: Plain text, Caesar, ROT13, Base64, XOR
"""

import requests
import json
import base64

BASE_URL = "https://barbara-ai-sooty.vercel.app/api/decrypt"

def test_cipher(name, payload):
    print(f"\n{'='*60}")
    print(f"🔐 Prueba: {name}")
    print(f"{'='*60}")
    print(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Método detectado: {data.get('method')}")
            print(f"📝 Resultado: {data.get('text')}")
            print(f"📊 Tipo: {data.get('file_type')}")
            if 'model_prediction' in data:
                print(f"🤖 Predicción ML: {data.get('model_prediction')}")
            return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("PRUEBAS DE DESENCRIPTACIÓN EN VERCEL")
    print("="*60)
    
    tests = [
        ("1️⃣ TEXTO PLANO", {"texto": "Hola mundo"}),
        
        ("2️⃣ CAESAR (shift 3: Khoor zruog)", 
         {"texto": "Khoor zruog", "method": "caesar", "key": 3}),
        
        ("3️⃣ ROT13 (Uryyb jbeyq)", 
         {"texto": "Uryyb jbeyq", "method": "rot13"}),
        
        ("4️⃣ BASE64 (SGVsbG8gd29ybGQ=)", 
         {"texto": "SGVsbG8gd29ybGQ=", "method": "base64"}),
        
        ("5️⃣ XOR (clave 42)", 
         {"texto": "Uryyb`iye!", "method": "xor", "key": 42}),
    ]
    
    results = []
    for name, payload in tests:
        success = test_cipher(name, payload)
        results.append((name, success))
    
    # Summary
    print(f"\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    for name, success in results:
        status = "✅ EXITOSO" if success else "❌ FALLIDO"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} pruebas exitosas")
    print("="*60)

if __name__ == "__main__":
    main()
