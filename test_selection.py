#!/usr/bin/env python3
"""Test the fixed decrypt logic"""

from api.index import attempt_decodings, english_score

def test_selection(text, name):
    """Simulate the new selection logic"""
    print(f"\n{'='*60}")
    print(f"🔧 Probando: {name}")
    print(f"{'='*60}")
    print(f"Entrada: {repr(text)}")
    
    attempts = attempt_decodings(text)
    
    # NEW LOGIC
    priority_order = ['rot13', 'caesar_shift', 'xor_1byte', 'base64', 'hex', 'raw']
    
    best_overall = None
    best_overall_score = 0
    scores = {}
    
    for pmethod in priority_order:
        candidates = []
        
        if pmethod == 'caesar_shift':
            candidates = [a for a in attempts if a['method'].startswith('caesar_shift') and a.get('text')]
        elif pmethod == 'xor_1byte':
            candidates = [a for a in attempts if a['method'].startswith('xor_1byte') and a.get('text')]
        else:
            candidates = [a for a in attempts if a['method'].startswith(pmethod) and a.get('text')]
        
        for a in candidates:
            score = english_score(a.get('text') or '')
            scores[a['method']] = score
            if score > best_overall_score:
                best_overall_score = score
                best_overall = a
    
    print(f"\n📊 Scores (top 10):")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    for method, score in sorted_scores:
        marker = "🎯" if best_overall and best_overall['method'] == method else "  "
        print(f"  {marker} {method}: {score}")
    
    if best_overall and best_overall_score > 2:
        print(f"\n✅ SELECCIONADO (score > 2): {best_overall['method']}")
        print(f"   Resultado: '{best_overall['text']}'")
    else:
        print(f"\n❌ No encontrado score > 2, usando fallback")

# Test cases
print("🔄 PRUEBAS DE AUTO-DETECCIÓN CON NUEVA LÓGICA")

test_selection("Uryyb jbeyq", "ROT13")
test_selection("Khoor zruog", "Caesar (shift 3)")

# XOR test
text = "Hello world"
key = 42
xor_bytes = bytes([ord(c) ^ key for c in text])
xor_text = xor_bytes.decode('latin-1')
test_selection(xor_text, f"XOR (clave {key})")

test_selection("Hola mundo", "Texto plano")
test_selection("SGVsbG8gd29ybGQ=", "Base64")
