# Secure File Encryption and Decryption System (SecureVault)

A modern, high-security, dark-themed offline desktop application built in **Python 3.12+** using **Tkinter** and **SQLite**. The system allows users to secure files of any format using **AES symmetric encryption (via Fernet)**, derived keys via **PBKDF2 key stretching**, and salted **SHA-256 password hashing** for credential authentication.

---

## 🚀 Key Features

*   **Secure File Encryption**: Protect files of any type (PDF, PNG, DOCX, ZIP, MP4, etc.) as encrypted `.enc` files.
*   **Secure File Decryption**: Decrypt `.enc` files back to their original formats.
*   **PBKDF2 Key Derivation**: Derives symmetric keys using PBKDF2 with 100,000 iterations of SHA-256 and a random 16-byte salt, protecting against brute-force attacks.
*   **Credential Protection**: Stores local user passwords as salted SHA-256 hashes in a local SQLite database.
*   **Authenticated Encryption**: Fernet uses HMAC-SHA256 signatures to verify file integrity and authenticity before decryption.
*   **Responsive Multi-threaded GUI**: Cryptographic and database operations are delegated to background threads to keep the UI responsive.
*   **Structured Audit Logging**: Logs system events and errors, with filter and search options inside the UI.
*   **Full Test Coverage**: Includes 11 automated unit and integration tests to ensure system stability.

---

## 🛠️ Installation and Setup

### Prerequisites
*   Python 3.12 or higher installed on your system.
*   Pip package manager.

### Step 1: Set Up a Virtual Environment (Optional but Recommended)
Open your terminal in the `SecureFileEncryptor` directory and run:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies
Install the required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
Start the application using:

```bash
python main.py
```

---

## 🧪 Running the Tests
SecureVault includes automated unit and integration tests that validate the security, database, and GUI components:

```bash
python -m unittest discover -s tests -v
```

---

## 📦 Building a Standalone Executable
You can package the application into a standalone Windows executable (`.exe`) that runs without requiring a Python installation.

Compile the application using **PyInstaller**:

```bash
pyinstaller --onefile --windowed main.py
```

After the build process completes successfully:
*   The standalone executable will be located in the `dist/` directory as `main.exe`.
*   You can distribute `dist/main.exe` directly to other Windows systems.
