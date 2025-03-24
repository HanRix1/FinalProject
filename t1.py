from cryptography.fernet import Fernet

secret_key = Fernet.generate_key()
secret_key_str = secret_key.decode()

print(f"SECRET_KEY={secret_key_str}")