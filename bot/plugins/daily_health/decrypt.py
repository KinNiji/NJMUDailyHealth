from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt(file_path):
    with open(file_path, 'rb') as f:
        key, iv, encrypted_data = [f.read(x) for x in (16, AES.block_size, -1)]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    string_data = data.decode('utf-8')
    return string_data
