import os
import sys
import hmac
import hashlib

secret_key = bytes(os.getenv("SIGNATURE_SECRET_KEY", "secret"), 'utf-8')

# Read input into binary string
data = sys.stdin.readlines()
data = "".join(data).replace("\n", "")
data = bytes(data, 'utf-8')

# Generate HMAC-SHA256 signature
signature = hmac.new(secret_key, data, hashlib.sha256).hexdigest()

# Print signature without endline
print(signature.upper(), end='')
