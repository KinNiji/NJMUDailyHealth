from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes


def encrypt(string_data, file_path):
    data = bytes(string_data, encoding='utf-8')
    # 随机生成16位秘钥
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_data = cipher.encrypt((pad(data, AES.block_size)))

    with open(file_path, 'wb') as f:
        for x in (key, cipher.iv, encrypted_data):
            f.write(x)
