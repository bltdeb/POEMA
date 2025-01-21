# Script to generate a secure secret key for FLASK app. Used Claude AI here as well.
import secrets
secret_key = secrets.token_hex(16)
print(f"Here's your secure secret key: {secret_key}")