from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory
import joblib
import os
import numpy as np
import base64
import binascii
import urllib.parse
import string
import codecs

app = Flask(__name__)
CORS(app)

# Configuración de rutas para archivos en Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'modelo_tiroides.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')
ENC_MODEL_PATH = os.path.join(BASE_DIR, 'modelo_cifrado_mlp.pkl')
ENC_SCALER_PATH = os.path.join(BASE_DIR, 'scaler_cifrado.pkl')

# Cargar el cerebro de la IA
model = None
scaler = None
try:
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("✅ Recursos cargados correctamente")
    else:
        print("⚠️ Modelo principal o scaler no encontrados; endpoints de predicción estarán deshabilitados hasta que se provean.")
except Exception as e:
    print(f"❌ Error de carga: {str(e)}")

# Intentar cargar modelos de cifrado si existen
enc_model = None
enc_scaler = None
try:
    if os.path.exists(ENC_MODEL_PATH):
        enc_model = joblib.load(ENC_MODEL_PATH)
    if os.path.exists(ENC_SCALER_PATH):
        enc_scaler = joblib.load(ENC_SCALER_PATH)
    if enc_model is not None:
        print("✅ Modelo de cifrado cargado")
except Exception as e:
    print(f"❌ Error cargando modelo de cifrado: {e}")


def is_printable_text(b: bytes) -> bool:
    try:
        s = b.decode('utf-8')
    except Exception:
        return False
    # consider printable if > 90% printable chars
    printable = sum(c in string.printable for c in s)
    return (printable / max(len(s), 1)) > 0.9


def caesar_shift(s: str, shift: int) -> str:
    def shift_char(c):
        if 'a' <= c <= 'z':
            return chr((ord(c) - ord('a') - shift) % 26 + ord('a'))
        if 'A' <= c <= 'Z':
            return chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
        return c
    return ''.join(shift_char(c) for c in s)


def xor_bytes_with_key(data: bytes, key_bytes: bytes) -> bytes:
    if not key_bytes:
        return data
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key_bytes[i % len(key_bytes)])
    return bytes(out)


def detect_file_type(b: bytes) -> str:
    if b.startswith(b'%PDF'):
        return 'PDF'
    if b.startswith(b'\x89PNG'):
        return 'PNG'
    if b.startswith(b'\xff\xd8'):
        return 'JPG'
    if b.startswith(b'GIF87a') or b.startswith(b'GIF89a'):
        return 'GIF'
    if b.startswith(b'PK'):
        return 'ZIP/Office (docx, xlsx, pptx)'
    if b.startswith(b'MZ'):
        return 'EXE/DLL (PE)'
    # plain text heuristic
    if is_printable_text(b):
        return 'Plain text'
    return 'Unknown/binary'


def attempt_decodings(text: str):
    attempts = []

    # raw text
    raw_bytes = text.encode('utf-8', errors='ignore')
    attempts.append({'method': 'raw', 'ok': True, 'bytes': raw_bytes, 'text': text, 'file_type': detect_file_type(raw_bytes)})

    # base64
    try:
        b = base64.b64decode(text, validate=True)
        attempts.append({'method': 'base64', 'ok': True, 'bytes': b, 'text': None, 'file_type': detect_file_type(b)})
        try:
            attempts[-1]['text'] = b.decode('utf-8')
        except Exception:
            attempts[-1]['text'] = None
    except Exception:
        pass

    # hex
    try:
        b = binascii.unhexlify(text.strip())
        attempts.append({'method': 'hex', 'ok': True, 'bytes': b, 'text': None, 'file_type': detect_file_type(b)})
        try:
            attempts[-1]['text'] = b.decode('utf-8')
        except Exception:
            attempts[-1]['text'] = None
    except Exception:
        pass

    # url decode
    try:
        s = urllib.parse.unquote_plus(text)
        b = s.encode('utf-8')
        attempts.append({'method': 'url', 'ok': True, 'bytes': b, 'text': s, 'file_type': detect_file_type(b)})
    except Exception:
        pass

    # rot13
    try:
        s = codecs.decode(text, 'rot_13')
        b = s.encode('utf-8')
        attempts.append({'method': 'rot13', 'ok': True, 'bytes': b, 'text': s, 'file_type': detect_file_type(b)})
    except Exception:
        pass

    # caesar brute-force (shifts 1..25)
    try:
        for shift in range(1, 26):
            s = caesar_shift(text, shift)
            b = s.encode('utf-8', errors='ignore')
            # consider plausible if largely printable
            if is_printable_text(b):
                attempts.append({'method': f'caesar_shift_{shift}', 'ok': True, 'bytes': b, 'text': s, 'file_type': detect_file_type(b)})
    except Exception:
        pass

    # XOR brute force (single-byte keys) - collect a few good candidates
    try:
        tb = text.encode('latin-1', errors='ignore')
        xor_found = 0
        for key in range(1, 256):
            b = bytes([c ^ key for c in tb])
            if is_printable_text(b):
                s = b.decode('utf-8', errors='ignore')
                attempts.append({'method': f'xor_1byte_key_{key}', 'ok': True, 'bytes': b, 'text': s, 'file_type': detect_file_type(b)})
                xor_found += 1
                if xor_found >= 5:
                    break
    except Exception:
        pass

    return attempts


def english_score(s: str) -> int:
    if not s:
        return 0
    low = s.lower()
    common = ['hello', 'world', 'the', 'and', 'is', 'secret', 'secreto', 'hola', 'mundo', 'prueba']
    score = 0
    for w in common:
        if w in low:
            score += 2
    # reward spaces (multi-word)
    score += low.count(' ') 
    return score


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = {}
    for b in data:
        freq[b] = freq.get(b, 0) + 1
    import math
    ent = 0.0
    length = len(data)
    for v in freq.values():
        p = v / length
        ent -= p * math.log2(p)
    return ent


def extract_features(text: str, attempts: list):
    # features: length, unique_chars, printable_ratio, entropy, has_base64, has_hex, url_printable, rot13_printable, xor_printable
    raw = text.encode('utf-8', errors='ignore')
    length = len(raw)
    unique_chars = len(set(raw))
    printable_ratio = sum(c in string.printable for c in text) / max(len(text), 1)
    entropy = shannon_entropy(raw)

    has_base64 = 0
    has_hex = 0
    url_printable = 0
    rot13_printable = 0
    xor_printable = 0

    for a in attempts:
        m = a.get('method', '')
        if m == 'base64' and a.get('bytes'):
            has_base64 = 1
        if m == 'hex' and a.get('bytes'):
            has_hex = 1
        if m == 'url' and a.get('text'):
            url_printable = 1
        if m == 'rot13' and a.get('text'):
            rot13_printable = 1
        if m.startswith('xor_1byte') and a.get('text'):
            xor_printable = 1

    # additional simple metrics
    null_bytes = raw.count(b"\x00")
    avg_byte = sum(raw)/max(len(raw),1) if raw else 0

    return [
        float(length),
        float(unique_chars),
        float(printable_ratio),
        float(entropy),
        float(has_base64),
        float(has_hex),
        float(url_printable),
        float(rot13_printable),
        float(xor_printable),
        float(null_bytes),
        float(avg_byte)
    ]

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
        if model is None or scaler is None:
            return jsonify({'status': 'error', 'message': 'Modelo o scaler no cargados en el servidor'}), 500
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]
        
        # Mapeo según el dataset original (1: Normal, 2: Hiper, 3: Hipo)
        mapping = {1: "Normal", 2: "Hipertiroidismo", 3: "Hipotiroidismo"}
        resultado = mapping.get(int(prediction), "Desconocido")
        
        return jsonify({'status': 'success', 'diagnostico': resultado})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    try:
        data = request.json
        text = data.get('texto') or data.get('text') or ''
        if not text:
            return jsonify({'status': 'error', 'message': 'No text provided'}), 400

        # allow targeted method/key from client
        method = (data.get('method') or '').lower()
        key = data.get('key')

        # If explicit caesar with key provided
        if method == 'caesar' and key is not None:
            try:
                shift = int(key) % 26
                s = caesar_shift(text, shift)
                b = s.encode('utf-8', errors='ignore')
                attempts = [{'method': f'caesar_shift_{shift}', 'ok': True, 'bytes': b, 'text': s, 'file_type': detect_file_type(b)}]
            except Exception:
                attempts = attempt_decodings(text)
        # If explicit xor with key provided
        elif method == 'xor' and key is not None:
            try:
                # numeric single-byte key
                if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
                    k = int(key) % 256
                    tb = text.encode('latin-1', errors='ignore')
                    b = bytes([c ^ k for c in tb])
                    s = b.decode('utf-8', errors='ignore')
                    attempts = [{'method': f'xor_1byte_key_{k}', 'ok': True, 'bytes': b, 'text': s, 'file_type': detect_file_type(b)}]
                else:
                    # assume key is string -> repeating-key XOR
                    kb = str(key).encode('latin-1', errors='ignore')
                    tb = text.encode('latin-1', errors='ignore')
                    b = xor_bytes_with_key(tb, kb)
                    s = b.decode('utf-8', errors='ignore')
                    attempts = [{'method': f'xor_repeating_key_{key}', 'ok': True, 'bytes': b, 'text': s, 'file_type': detect_file_type(b)}]
            except Exception:
                attempts = attempt_decodings(text)
        else:
            attempts = attempt_decodings(text)

        # pick best attempt: prioritize by method effectiveness
        # priority order: base64 > hex > raw > caesar > rot13 > xor > url
        priority_order = ['base64', 'hex', 'raw', 'caesar_shift', 'rot13', 'xor_1byte']

        chosen = None
        # try priority methods first (match by prefix)
        for pmethod in priority_order:
            # special handling for caesar: choose best-scoring candidate among shifts
            if pmethod == 'caesar_shift':
                caesars = [a for a in attempts if a['method'].startswith('caesar_shift') and a.get('text')]
                if caesars:
                    best = None
                    best_score = -1
                    for a in caesars:
                        s = a.get('text') or ''
                        sc = english_score(s)
                        if sc > best_score:
                            best_score = sc
                            best = a
                    if best is not None and best_score > 0:
                        chosen = best
                        break
                    # fallback: pick the caesar with most letters
                    if best is None:
                        best = caesars[0]
                    else:
                        chosen = best
                        break
                continue

            for a in attempts:
                if a['method'].startswith(pmethod) and a.get('text'):
                    chosen = a
                    break
            if chosen:
                break

        # if no priority method worked, try any non-raw with text
        if chosen is None:
            for a in attempts:
                if a['method'] != 'raw' and a.get('text'):
                    chosen = a
                    break

        # if still no match, try any known file type
        if chosen is None:
            for a in attempts:
                if a.get('file_type') and a['file_type'] != 'Unknown/binary' and a['method'] != 'raw':
                    chosen = a
                    break

        # fallback to raw
        if chosen is None:
            chosen = attempts[0] if attempts else {'method': 'none', 'text': None, 'file_type': 'Unknown'}

        # prepare response
        resp = {
            'status': 'success',
            'method': chosen.get('method'),
            'file_type': chosen.get('file_type'),
            'text': chosen.get('text') if chosen.get('text') is not None else None,
            'bytes_base64': base64.b64encode(chosen.get('bytes', b'')).decode('ascii') if chosen.get('bytes') is not None else None,
            'attempts': [{'method': a['method'], 'file_type': a.get('file_type'), 'has_text': bool(a.get('text'))} for a in attempts]
        }

        # If we have an encryption model and scaler, extract features and predict
        if enc_model is not None and enc_scaler is not None:
            try:
                feats = extract_features(text, attempts)
                # adapt features length to what the scaler expects (pad with zeros or truncate)
                expected = getattr(enc_scaler, 'n_features_in_', None)
                feats_adj = list(feats)
                if expected is not None:
                    if len(feats_adj) < expected:
                        feats_adj += [0.0] * (expected - len(feats_adj))
                    elif len(feats_adj) > expected:
                        feats_adj = feats_adj[:expected]
                X = enc_scaler.transform([feats_adj])
                pred = enc_model.predict(X)
                resp['model_prediction'] = str(pred[0])
                # try to include confidence if available
                if hasattr(enc_model, 'predict_proba'):
                    probs = enc_model.predict_proba(X)[0]
                    resp['model_confidence'] = float(max(probs))
            except Exception as e:
                resp['model_error'] = str(e)

        return jsonify(resp)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/', methods=['GET'])
def serve_index():
    # serve the project's index.html so the UI can call the API on localhost
    root_dir = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
    return send_from_directory(root_dir, 'index.html')


@app.route('/index.html', methods=['GET'])
def serve_index_alias():
    return serve_index()