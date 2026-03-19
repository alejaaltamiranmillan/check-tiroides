#!/usr/bin/env python3
"""Debug script to test attempt_decodings() function"""

from api.index import attempt_decodings, english_score

# Prueba 1: ROT13
print("🔴 Prueba 1: ROT13")
text_rot13 = "Uryyb jbeyq"  # "Hello world" en ROT13
attempts = attempt_decodings(text_rot13)
print(f"  Entrada: {text_rot13}")
for a in attempts:
    if a.get('text'):
        score = english_score(a.get('text'))
        print(f"  - {a['method']}: '{a['text']}' (score: {score})")

print("\n🔴 Prueba 2: Caesar (shift 3)")
text_caesar = "Khoor zruog"  # "Hello world" con shift 3
attempts = attempt_decodings(text_caesar)
print(f"  Entrada: {text_caesar}")
for a in attempts:
    if a.get('text'):
        score = english_score(a.get('text'))
        print(f"  - {a['method']}: '{a['text']}' (score: {score})")

print("\n🔴 Prueba 3: XOR (clave 42)")
text = "Hello world"
key = 42
xor_bytes = bytes([ord(c) ^ key for c in text])
xor_text = xor_bytes.decode('latin-1')
attempts = attempt_decodings(xor_text)
print(f"  Entrada: {repr(xor_text)}")
print(f"  Buscando decodificación XOR...")
xor_found = [a for a in attempts if 'xor' in a['method']]
if xor_found:
    for a in xor_found:
        print(f"  - {a['method']}: '{a.get('text', 'N/A')}'")
else:
    print(f"  ❌ No se encontraron intentos XOR")
    print(f"  Todos los intentos:")
    for a in attempts:
        print(f"    - {a.get('method')}: text={bool(a.get('text'))}")
