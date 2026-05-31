# CLI File Encryptor

A production-grade, secure File Encryption and Decryption application built in Python. This tool uses `cryptography.fernet` (AES symmetric encryption) and supports both single-file processing and batch directory processing.

## Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Setup Instructions

1. **Navigate to the directory**:
   ```bash
   cd CLIFileEncryptor
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate an Encryption Key**:
   Before you can encrypt or decrypt files, you must generate a secure key. This will create a `secret.key` file in the directory.
   ```bash
   python app.py generate-key
   ```
   > **WARNING**: DO NOT lose or share this `secret.key` file. Anyone with this file can decrypt your data. If you lose it, you cannot recover your encrypted files. It is explicitly ignored in `.gitignore`.

## Usage Guide

You can view the help menu anytime by running:
```bash
python app.py --help
```

### 1. Encrypting Files

**Encrypt a Single File:**
```bash
python app.py encrypt --file "path/to/your/file.txt"
```
*This will create an encrypted copy named `file.txt.enc`.*

**Encrypt a Directory (Batch):**
```bash
python app.py encrypt --dir "path/to/your/folder"
```
*This recursively processes all files. Files that are already encrypted (ending in `.enc`) and the `secret.key` itself will be safely skipped.*

### 2. Decrypting Files

**Decrypt a Single File:**
```bash
python app.py decrypt --file "path/to/your/file.txt.enc"
```
*This will restore the original file by decrypting the content and removing the `.enc` extension.*

**Decrypt a Directory (Batch):**
```bash
python app.py decrypt --dir "path/to/your/folder"
```
*This recursively decrypts all `.enc` files in the folder.*
