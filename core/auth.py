import os
import json
import hashlib

CONFIG_FILE = "config.json"

def is_password_set():
    if not os.path.exists(CONFIG_FILE):
        return False
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return 'master_password_hash' in data
    except:
        return False

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def set_password(password):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                data = json.load(f)
            except:
                pass
    data['master_password_hash'] = hash_password(password)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)
    return True

def verify_password(password):
    if not is_password_set():
        return False
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
        return data.get('master_password_hash') == hash_password(password)
    except:
        return False
