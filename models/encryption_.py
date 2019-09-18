from cryptography.fernet import Fernet


def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message.encode())


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token).decode()


def Encrypt(data):
    key = Fernet.generate_key()
    enMessage = encrypt(data, key)
    return [enMessage, key]


def Decrypt(enMessage, key):
    deMessage = decrypt(enMessage, key)
    return deMessage
