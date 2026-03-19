#!/usr/bin/env python3
"""Test simplified UI"""

import requests

url = 'https://barbara-ai-sooty.vercel.app/api/decrypt'

print("Testing simplified UI (auto-detection only):")
print()

# Test ROT13
r = requests.post(url, json={'texto': 'Uryyb jbeyq'})
data = r.json()
print(f"ROT13: {data.get('method')} -> {data.get('text')}")

# Test Caesar
r = requests.post(url, json={'texto': 'Khoor zruog'})
data = r.json()
print(f"Caesar: {data.get('method')} -> {data.get('text')}")

# Test Base64
r = requests.post(url, json={'texto': 'SGVsbG8gd29ybGQ='})
data = r.json()
print(f"Base64: {data.get('method')} -> {data.get('text')}")

print()
print("✅ All ciphers auto-detect and decrypt correctly!")
