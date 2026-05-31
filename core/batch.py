import os
from .crypto import encrypt_file, decrypt_file, KEY_FILE

def process_directory(dir_path, action="encrypt"):
    """
    Recursively processes all files in a directory.
    action can be 'encrypt' or 'decrypt'.
    """
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        return False, f"Directory not found or is not a directory: {dir_path}"

    results = {"success": 0, "skipped": 0, "failed": 0, "details": []}

    for root, _, files in os.walk(dir_path):
        for file in files:
            # Skip the secret key file itself to prevent encrypting our own key
            if file == KEY_FILE:
                results["skipped"] += 1
                results["details"].append(f"[SKIPPED] Refusing to touch key file: {file}")
                continue

            file_path = os.path.join(root, file)
            
            if action == "encrypt":
                # Skip if already encrypted
                if file.endswith('.enc'):
                    results["skipped"] += 1
                    results["details"].append(f"[SKIPPED] Already encrypted: {file_path}")
                    continue
                success, msg = encrypt_file(file_path)
            elif action == "decrypt":
                # Skip if not encrypted
                if not file.endswith('.enc'):
                    results["skipped"] += 1
                    results["details"].append(f"[SKIPPED] Not an encrypted file: {file_path}")
                    continue
                success, msg = decrypt_file(file_path)
            else:
                return False, f"Invalid action: {action}"

            if success:
                results["success"] += 1
                results["details"].append(f"[SUCCESS] {msg}")
            else:
                results["failed"] += 1
                results["details"].append(f"[FAILED] {msg}")

    return True, results
