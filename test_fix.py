#!/usr/bin/env python3
"""Test the fixed scoring"""

from api.index import attempt_decodings, english_score

texto = 'ubl rf whrirf fbpvny'
print(f'Testing: {texto}')
print()

attempts = attempt_decodings(texto)

# Find best one using the new selection logic
priority_order = ['rot13', 'caesar_shift', 'xor_1byte', 'base64', 'hex', 'raw']
best = None
best_score = 0

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
        if score > best_score:
            best_score = score
            best = a

if best:
    print(f'BEST: {best["method"]} (score {best_score})')
    print(f'Result: {best["text"]}')
else:
    print('No result found')
