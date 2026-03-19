#!/usr/bin/env python3
"""Test decrypt endpoint directly"""

from api.index import attempt_decodings, english_score

def select_best(text_input):
    """Simulate the decrypt endpoint selection logic"""
    attempts = attempt_decodings(text_input)
    
    # Replicar la nueva lógica de selección
    priority_order = ['rot13', 'caesar_shift', 'xor_1byte', 'base64', 'hex', 'raw']
    best_overall = None
    best_overall_score = 0
    
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
            if score > best_overall_score:
                best_overall_score = score
                best_overall = a
    
    return best_overall, best_overall_score

# Test cases
tests = [
    ("Uryyb jbeyq", "ROT13", "Hello world"),
    ("Khoor zruog", "Caesar", "Hello world"),
    ("SGVsbG8gd29ybGQ=", "Base64", "Hello world"),
]

# XOR test
text = "Hello world"
key = 42
xor_bytes = bytes([ord(c) ^ key for c in text])
xor_text = xor_bytes.decode('latin-1')
tests.append((xor_text, "XOR key 42", text))

print("="*60)
print("TESTING DECRYPTION SELECT LOGIC")
print("="*60)

for input_text, name, expected in tests:
    result, score = select_best(input_text)
    if result:
        success = "✅" if result['text'] == expected else "❌"
        print(f"\n{success} {name}")
        print(f"   Method: {result['method']}")
        print(f"   Result: {result['text']}")
        print(f"   Score: {score}")
    else:
        print(f"\n❌ {name}")
        print(f"   No result found")
