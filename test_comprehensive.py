#!/usr/bin/env python3
"""Final comprehensive test"""

import requests

url = 'https://barbara-ai-sooty.vercel.app/api/decrypt'

tests = [
    ('ubl rf whrirf fbpvny', 'ROT13 (Spanish)', 'hoy es jueves social'),
    ('Uryyb jbeyq', 'ROT13 (English)', 'Hello world'),
    ('Khoor zruog', 'Caesar shift 3', 'Hello world'),
    ('SGVsbG8gd29ybGQ=', 'Base64', 'Hello world'),
    ('Hola mundo', 'Plain text', 'Hola mundo'),
]

print("="*60)
print("FINAL COMPREHENSIVE TEST")
print("="*60)
print()

passed = 0
failed = 0

for encoded, cipher_type, expected in tests:
    try:
        r = requests.post(url, json={'texto': encoded}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            result = data.get('text')
            method = data.get('method')
            
            if result == expected:
                print(f"✅ {cipher_type}")
                print(f"   Method: {method}")
                print(f"   Result: {result}")
                passed += 1
            else:
                print(f"❌ {cipher_type}")
                print(f"   Expected: {expected}")
                print(f"   Got: {result}")
                failed += 1
        else:
            print(f"❌ {cipher_type} - HTTP {r.status_code}")
            failed += 1
    except Exception as e:
        print(f"❌ {cipher_type} - {str(e)}")
        failed += 1
    print()

print("="*60)
print(f"Results: {passed} passed, {failed} failed")
print("="*60)
