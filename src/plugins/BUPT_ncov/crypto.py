import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

from typing import Tuple
from pathlib import Path


def msg_encrypt(passwd: str, secret: bytes, iv: bytes):
    msg = passwd.encode()
    aes = AES.new(secret, mode=AES.MODE_CFB, iv=iv)
    encrypted_pass = aes.encrypt(msg)
    return base64.b64encode(encrypted_pass).decode()


def msg_decrypt(enc_passwd: str, secret: bytes, iv: bytes):
    msg = base64.b64decode(enc_passwd)
    aes = AES.new(secret, mode=AES.MODE_CFB, iv=iv)
    passwd = aes.decrypt(msg)
    return passwd.decode()


def get_passwd_secret_iv(path: Path,
                         file_name: str,
                         passwd: str = None,
                         salt: bytes = None,
                         force: bool = False
                         ) -> Tuple[bytes, bytes]:
    if force or not Path.exists(path / file_name):
        secret = PBKDF2(passwd, salt, 32)
        cipher = AES.new(secret, mode=AES.MODE_CFB)
        iv = cipher.iv
        with open(path / file_name, "wb") as f:
            f.writelines([secret, iv])
    else:
        with open(path / file_name, "rb") as f:
            secret, iv = f.read(32), f.read(16)
    return secret, iv


def initialize(path: Path) -> bytes:
    if not Path.exists(path):
        with open(path, 'wb') as f:
            f.write(get_random_bytes(32))
    with open(path, 'rb') as f:
        salt = f.read()
    return salt



