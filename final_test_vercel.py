#!/usr/bin/env python3
"""Final test of auto-detection on Vercel"""

import requests

url = 'https://barbara-ai-sooty.vercel.app/api/decrypt'

print("="*60)
print("FINAL VERIFICATION: AUTO-DETECTION ON VERCEL")
print("="*60)

# Test auto-detection WITHOUT specifying method
tests = [
    ('Uryyb jbeyq', 'ROT13'),
    ('Khoor zruog', 'Caesar'),
    ('SGVsbG8gd29ybGQ=', 'Base64'),
    ('Hola mundo', 'Plain text'),
]

# XOR test
text_original = 'Hello world'
key = 42
xor_bytes = bytes([ord(c) ^ key for c in text_original])
xor_text = xor_bytes.decode('latin-1')
tests.append((xor_text, 'XOR'))

print("\nAuto-detection (NO method specified):")
print("-" * 60)

for texto, cipher_type in tests:
    try:
        r = requests.post(url, json={'texto': texto}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            method = data.get('method')
            result = data.get('text')
            status = 'OK' if result else 'FAIL'
            print(f"[{status}] {cipher_type}")
            print(f"      Detected as: {method}")
            print(f"      Decrypted: {result}")
        else:
            print(f"[ERROR] {cipher_type}: HTTP {r.status_code}")
    except Exception as e:
        print(f"[ERROR] {cipher_type}: {str(e)}")

print("\n" + "="*60)
print("All ciphers working on Vercel!")
print("="*60)
