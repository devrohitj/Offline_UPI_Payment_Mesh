import os
import base64
import hashlib

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

def encrypt_payload(data: bytes):
    aes_key = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(aes_key)
    iv=os.urandom(12)
    ciphertext=aes.encrypt(iv,data,None)

    encrypted_key=public_key.encrypt(aes_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))

    combined = encrypted_key + iv + ciphertext

    return base64.b64encode(combined).decode() #decode converts bytes-->str

def decrypt_payload(blob: str):

    #raw =[ encrypted_key ][ iv ][ ciphertext ]

    raw = base64.b64decode(blob) #converts str-->bytes 
    encrypted_key = raw[:256] #RSA-2048 = 2048 bits = 256 bytes
    iv = raw[256:268] #GCM IV = 12 bytes
    ciphertext = raw[268:] #Everything remaining is: AES ciphertext + GCM auth tag
    
    #NOTE:Remember:GCM automatically appends the authentication tag internally.So we don't manually separate it.The cryptography library handles that.

    aes_key=private_key.decrypt(encrypted_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))

    aes = AESGCM(aes_key)

    plaintext=aes.decrypt(iv,ciphertext,None)

    return plaintext

def hash_ciphertext(blob: str):
    data = blob.encode() #converts str-->bytes
    digest = hashlib.sha256(data).hexdigest()
    return digest


    
