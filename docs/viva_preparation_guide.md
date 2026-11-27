# Viva Voce Preparation Guide: Secure File Encryption & Decryption System

This guide contains 50 rigorous viva questions and detailed answers designed to prepare you for your project presentation, defense, and examination. The questions are organized into four core domains: Cryptography & Security, Software Engineering & OOP, Database Design, and GUI & Multi-threading.

---

## Part 1: Cryptography & Security (Questions 1 - 18)

### Q1: What is the difference between symmetric and asymmetric encryption, and which one does this system use?
**Answer:** Symmetric encryption uses a single, shared secret key for both the encryption of plaintext and the decryption of ciphertext. It is highly efficient and suitable for large payloads. Asymmetric encryption uses a mathematically linked key pair: a public key for encryption and a private key for decryption. This system uses **symmetric encryption** (via the Fernet standard of AES) because it is designed to encrypt local user files efficiently.

### Q2: What is the Fernet standard, and what underlying cryptographic primitives does it employ?
**Answer:** Fernet is a secure specification for authenticated symmetric encryption. It guarantees that data encrypted cannot be read or modified without the key. Under the hood, Fernet uses:
1. **AES (Advanced Encryption Standard)** in CBC (Cipher Block Chaining) mode with a 128-bit key for ciphertext generation.
2. **HMAC (Hash-based Message Authentication Code)** with SHA-256 for integrity verification and authenticity checking.
3. **PKCS7 Padding** to pad the plaintext to 16-byte block sizes.
4. **Initialization Vector (IV)** generated randomly for each block operation to prevent pattern matching.

### Q3: Why did you choose PBKDF2 instead of directly hashing the user password to generate the encryption key?
**Answer:** Plain text passwords are often short and low-entropy, making them highly vulnerable to brute-force and dictionary attacks if hashed directly. **PBKDF2 (Password-Based Key Derivation Function 2)** is a key-stretching algorithm. It applies a pseudorandom function (like HMAC-SHA256) repeatedly (100,000 iterations in our system) along with a unique salt to the password. This computational cost makes brute-forcing derived keys exponentially slower, dramatically improving security against offline dictionary attacks.

### Q4: Explain the role and significance of a "Cryptographic Salt" in password hashing and key derivation.
**Answer:** A salt is a sequence of cryptographically secure random bytes generated for each specific password hash or key derivation operation. 
- In **password hashing**, the salt ensures that two users with identical passwords will have completely different stored hashes, rendering precomputed lookup tables (Rainbow Tables) useless.
- In **key derivation**, the salt ensures that if a user encrypts two identical files with the same password, they produce entirely distinct ciphers, masking data patterns.

### Q5: What is SHA-256, and where is it utilized in this application?
**Answer:** SHA-256 (Secure Hash Algorithm, 256-bit) is a one-way cryptographic hash function that maps an input of arbitrary length to a fixed-size 256-bit signature. In this application, it is used for:
1. **User Authentication Hashing**: To store salted password hashes in the database: `Hex(SHA256(Salt || Password))`.
2. **File Integrity Checksums**: In both the history logger and test cases, to verify if a decrypted file matches the original plaintext hash exactly.

### Q6: How does the system protect against the "Brute-force" guessing of passwords?
**Answer:** Brute-force protection is enforced by two complementary layers:
1. **PBKDF2 Iterations**: By setting iterations to 100,000, deriving the key takes a fraction of a second on modern consumer hardware. This is unnoticeable to a legitimate user but makes high-speed hardware-accelerated brute-forcing (e.g., using GPUs) computationally expensive and impractical.
2. **User Lockouts**: The database layer tracks failed authentication attempts and blocks logins if a threshold is crossed (customizable in settings).

### Q7: If someone obtains a copy of your SQLite database file (`secure_vault.db`), can they decrypt the encrypted files?
**Answer:** **No.** The database stores salted user login hashes, audit logs, and file metadata history. It does **not** store the file encryption passwords or the derived symmetric keys. Without the user entering the correct session-specific password, the derived key cannot be reconstructed, meaning the encrypted files remain completely secure.

### Q8: What is "Authenticated Encryption" and how does the system achieve it?
**Answer:** Authenticated encryption is a security property that simultaneously guarantees confidentiality, integrity, and authenticity of the data. The system achieves this via **Fernet (AES-CBC + HMAC-SHA256)**. When decrypting, Fernet verifies the HMAC signature of the ciphertext *before* attempting decryption. If even one bit of the ciphertext or salt is tampered with, the HMAC verification fails, raising an `InvalidToken` exception.

### Q9: Where does the system store the salt used to encrypt individual files?
**Answer:** The salt is stored directly within the header of the encrypted file itself. For every file operation, a unique 16-byte random salt is generated. During encryption, these 16 bytes are prepended to the ciphertext. During decryption, the system reads the first 16 bytes from the encrypted file as the salt, derives the key using the password, and decrypts the remainder of the file.

### Q10: Why is it safe to store the encryption salt in plaintext at the beginning of the file?
**Answer:** Salt does not need to be secret; its only purpose is to ensure uniqueness. The security of PBKDF2 and AES rests on the entropy of the user's password, not the secrecy of the salt. Knowing the salt only allows an attacker to build a custom dictionary attack for that single password, which is already mitigated by the 100,000 iteration stretching cost.

### Q11: What happens if a single byte in an encrypted file is corrupted?
**Answer:** If even one byte of the encrypted file is altered, the HMAC authentication tag embedded in the Fernet envelope will fail to match the calculated hash. The `cryptography` library will raise an `InvalidToken` error, and our application will catch it and display an "Integrity Verification Failed" message to protect the user from processing corrupted plaintexts.

### Q12: Why is `os.urandom()` preferred over Python's standard `random` module for generating salts?
**Answer:** The standard `random` module uses the Mersenne Twister algorithm, which is a pseudo-random number generator (PRNG). Its outputs are entirely deterministic and predictable once the state is observed. `os.urandom()` queries the underlying operating system's cryptographic source (like Windows CryptoAPI or `/dev/urandom` in Unix), which collects physical hardware entropy. This ensures true cryptographic randomness, making salts unpredictable.

### Q13: What is "Key Stretching"?
**Answer:** Key stretching is the technique of converting a weak key or short password into a longer, more secure key by running it through a resource-intensive cryptographic loop. Algorithms like PBKDF2 stretch keys by running thousands of iterations of a hash function, forcing attackers to spend significantly more CPU cycles per password guess.

### Q14: How does this system handle padding?
**Answer:** AES is a block cipher that operates on fixed-size blocks of 16 bytes (128 bits). If a file's size is not a multiple of 16 bytes, it must be padded. The system handles padding transparently using the **PKCS7** standard, which is integrated directly into the `cryptography.fernet` implementation.

### Q15: What is an Initialization Vector (IV), and how is it used in CBC mode?
**Answer:** An Initialization Vector (IV) is a block of random data used to initialize the first block of encryption in Cipher Block Chaining (CBC) mode. Each block of plaintext is XORed with the previous block of ciphertext before being encrypted. For the first block, there is no previous ciphertext, so it is XORed with the IV. This ensures that identical files encrypted with the exact same key produce different ciphertexts.

### Q16: Can this system encrypt and decrypt huge files (e.g., 10 GB movies)?
**Answer:** Yes, but because the standard `Fernet` implementation reads the entire file into system memory during encryption/decryption, processing files larger than the available physical RAM would cause high memory pressure. For production environments handling multi-gigabyte files, a chunk-based AES streaming approach (using `cryptography.hazmat.primitives.ciphers`) is preferred.

### Q17: What is a Rainbow Table, and how does your system neutralize it?
**Answer:** A Rainbow Table is a precomputed lookup table of passwords and their corresponding hashes, used to crack password hashes instantly. Our system neutralizes Rainbow Tables by using a **16-byte random salt** for every password hash. An attacker would have to compute a unique rainbow table for every single unique salt value, which is computationally impossible.

### Q18: What is the length of a SHA-256 hash in bits, bytes, and hexadecimal characters?
**Answer:** A SHA-256 hash is **256 bits** in length, which translates to **32 bytes**. When represented as a hexadecimal string, it is **64 characters** long (since each byte is represented by two hexadecimal characters).

---

## Part 2: Software Architecture & OOP (Questions 19 - 30)

### Q19: Explain the architectural pattern used in this project.
**Answer:** This project is built using a **Modular, Layered Architecture** inspired by the MVC (Model-View-Controller) design pattern:
1. **Model (Database Layer)**: Custom database scripts (`manager.py`) manage direct read/write transactions.
2. **View (GUI Layer)**: Individual Tkinter modules in `gui/pages/` render elements on screen.
3. **Controller (App Layer)**: The `SecureVaultApp` class coordinates page routing, manages session dictionaries, and updates global assets.
4. **Service (Security Layer)**: The `SecureEncryptor` class operates as a stateless utility service.

### Q20: What are the benefits of organizing the project into separate modules (folders like config, gui, security, database)?
**Answer:** Organising the codebase into distinct modules improves:
- **Separation of Concerns (SoC)**: Each component has a single responsibility.
- **Maintainability**: Bugs in the cryptography layer can be fixed without touching the UI layouts.
- **Testability**: Independent unit tests can be written for the database and cryptography layers without initializing a GUI mainloop.
- **Reusability**: The database and security modules can be integrated into a web API or CLI client with zero changes.

### Q21: What is Object-Oriented Programming (OOP) and how is it utilized in the GUI design?
**Answer:** OOP is a programming paradigm based on the concept of "objects," which contain data (attributes) and code (methods). In the GUI:
- All pages inherit from `tkinter.Frame` (Inheritance).
- Polymorphism allows the controller to call `show_page` on different classes uniformly.
- Encapsulation hides private UI helpers, exposing only standard handlers.

### Q22: What is the role of `__init__.py` files in your directories?
**Answer:** In Python, `__init__.py` files designate a directory as an importable package. This allows us to import our submodules using clean namespaces like `from gui.pages.login import LoginPage`.

### Q23: Why did you make `SecureEncryptor` methods static?
**Answer:** The `SecureEncryptor` class operates as a pure utility or service layer. It does not maintain any internal instance state; all its operations (encrypting, decrypting, hashing) are stateless and depend entirely on the input parameters provided. Making them `@staticmethod` eliminates the need to instantiate the class, simplifying the code.

### Q24: How does the page routing mechanism work in your `SecureVaultApp` class?
**Answer:** The application acts as a single-window interface. It manages a dynamic container frame `content_container`. When `show_page(PageClass)` is called, the application destroys the old frame, instantiates the new `PageClass` as a child of the container, attaches it to the grid, and brings it into focus.

### Q25: What is the purpose of `requirements.txt`?
**Answer:** It acts as a standard dependency manifest. It lists the external libraries required to execute the application (like `cryptography` and `pyinstaller`) along with their compatible versions, allowing other developers to quickly set up their environment using `pip install -r requirements.txt`.

### Q26: Explain how you avoided tight coupling between the GUI classes and the Database layer.
**Answer:** We avoided tight coupling by instantiating `DatabaseManager` once inside `main.py` and passing it to the root application class `SecureVaultApp` via Dependency Injection. Individual pages then access the database by querying `self.controller.db` instead of instantiating their own database managers.

### Q27: How is exception handling designed in the backend operations?
**Answer:** Every database and security operation is wrapped in standard `try-except` blocks. If an operation fails (e.g. database locked, missing salt, wrong password), the low-level module captures the error, logs the traceback via `DatabaseManager.log_event`, and bubbles up a clean user-facing error message using `tkinter.messagebox`.

### Q28: What is "Dependency Injection"?
**Answer:** Dependency Injection is a design pattern where an object receives its dependencies from an external source rather than creating them itself. In our project, `DatabaseManager` is injected into `SecureVaultApp`, which in turn passes itself as a controller to all page frames, ensuring a single shared state.

### Q29: What is PKCS7 Padding, and why is it necessary?
**Answer:** PKCS7 padding is a method of adding padding bytes to a block of plaintext so that its length becomes a multiple of the block size (16 bytes for AES). If the last block is short by $N$ bytes, the value of $N$ is appended $N$ times. For example, if it's short by 3 bytes, `\x03\x03\x03` is appended. This allows the decryptor to instantly determine the exact padding length and strip it safely.

### Q30: How does Python's `sys.path` affect module imports in a nested directory structure?
**Answer:** `sys.path` contains the list of directories Python searches for modules. When running a project, the directory containing the entry script (`main.py`) is added to the root path. Because of this, nested subfolders like `gui/` or `security/` can easily import configurations using root-level namespaces like `import config.settings`.

---

## Part 3: Database Design (Questions 31 - 40)

### Q31: What database engine did you select for this project, and why?
**Answer:** We chose **SQLite** because it is a lightweight, serverless, self-contained, and file-based relational database system. It requires zero configuration, stores all records in a single local database file (`secure_vault.db`), and is highly performant for desktop applications.

### Q32: Explain the structure and relationship of the SQLite database tables.
**Answer:** The database defines three key tables:
1. `Users`: Stores local credentials (`id`, `username`, `password_hash`, `salt`, `created_at`).
2. `EncryptionHistory`: Tracks file operations (`id`, `user_id`, `action_type`, `original_filename`, `processed_filename`, `file_size`, `file_hash`, `timestamp`). It has a Foreign Key relationship pointing to `Users(id)`.
3. `Logs`: Stores debug and audit events (`id`, `level`, `message`, `module`, `timestamp`).

### Q33: Why did you choose `ORDER BY id DESC` instead of `ORDER BY timestamp DESC` for your history and log queries?
**Answer:** In fast-running database systems or unit tests, multiple transactions can occur in the same fraction of a second. Because SQLite's `CURRENT_TIMESTAMP` resolution is typically 1 second, sorting strictly by timestamp is non-deterministic for sub-second operations. Sorting by the primary key `id DESC` guarantees strict chronological ordering because `id` is a monotonically increasing autoincrement integer.

### Q34: What is a Foreign Key, and how is it used in this project?
**Answer:** A Foreign Key is a field in one table that uniquely identifies a row in another table, establishing a relationship. In this project, `EncryptionHistory.user_id` is a Foreign Key that links to the primary key `Users.id`, ensuring that each cryptographic operation is associated with a registered user account.

### Q35: What does `ON DELETE SET NULL` mean in the foreign key definition?
**Answer:** It is a referential integrity constraint. If a user account is deleted from the `Users` table, instead of deleting their history records (which might be needed for audits) or blocking the deletion, SQLite automatically sets the `user_id` field in `EncryptionHistory` to `NULL`.

### Q36: How does the application prevent SQL Injection attacks?
**Answer:** The application prevents SQL Injection by utilizing **Parameterized Queries** (placeholders like `?` in SQL statements) instead of string formatting or concatenation. For example:
`cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))`
This forces SQLite to treat user input strictly as data, never as executable SQL commands.

### Q37: How do you handle database connections safely to prevent resource leaks and locks?
**Answer:** SQLite connections are managed using Python's `contextlib.contextmanager` wrapper. The helper yields a connection context and guarantees that `conn.close()` is executed in a `finally` block. This releases active database locks and prevents "Database is locked" exceptions, especially on Windows operating systems.

### Q38: What is the role of `sqlite3.Row` in your connection settings?
**Answer:** Setting `conn.row_factory = sqlite3.Row` configures SQLite to return query results as dict-like row objects instead of plain tuples. This allows developers to access columns by name (e.g. `row["username"]`) instead of index positions (e.g. `row[1]`), improving code readability and maintainability.

### Q39: What is Database Normalization, and does your design follow it?
**Answer:** Normalization is the process of structuring a database to reduce data redundancy and improve data integrity. Our design follows **Third Normal Form (3NF)**:
- Users are isolated into a distinct table.
- History tables refer to user IDs instead of duplicating username string values.
- All non-key fields depend entirely on the primary keys of their respective tables.

### Q40: What happens to the database file if the application crashes unexpectedly?
**Answer:** SQLite uses a robust transactional logging system (using rollback journals or Write-Ahead Logging). If the application crashes during a write, the incomplete transaction is safely rolled back on the next database connection, preventing database corruption and ensuring data consistency.

---

## Part 4: GUI & Multi-Threading (Questions 41 - 50)

### Q41: Why is multi-threading crucial in GUI applications when performing file encryption?
**Answer:** Python's Tkinter runs on a single main thread (the event loop). If a heavy task like PBKDF2 key derivation or a large file encryption operation is executed on the main thread, it blocks the event loop, freezing the window and making the UI non-responsive. By delegating the encryption work to a background thread (`threading.Thread`), the main thread remains free to redraw the GUI, update progress bars, and handle user interactions.

### Q42: What is the Tkinter `mainloop()`?
**Answer:** `mainloop()` is an infinite loop that listens for window system events (mouse clicks, keyboard inputs, draw requests) and dispatches them to their respective event handlers. The program blocks at this call until the main window is closed.

### Q43: How did you implement custom modern dark themes using standard Tkinter primitives?
**Answer:** Since native Tkinter styling can look dated, we customized all element properties explicitly:
1. Disabled active Windows borders (`bd=0`, `highlightthickness=0`).
2. Configured custom color dictionaries (`bg='#121212'`, `fg='#E0E6ED'`).
3. Bound hover triggers (`<Enter>` and `<Leave>`) to widgets to shift background colors dynamically.
4. Styled cards using thin amethyst violet outlines to simulate modern glassmorphism panels.

### Q44: What are Tkinter event bindings, and how are they used in this system?
**Answer:** Event bindings map user actions (like key presses, hover states, and mouse clicks) to specific Python functions. For example:
- We bind `<Enter>` and `<Leave>` to animate our flat buttons.
- We bind `<Button-1>` (left-click) to custom label widgets to act as clickable buttons or toggles.

### Q45: How does your secure password field toggle visibility?
**Answer:** The custom `SecureInputField` encapsulates a standard `tk.Entry` widget alongside a clickable `tk.Label` eye icon ("👁"). When clicked, the label triggers a toggle helper that flips between setting the entry's `show` parameter to `"*"` (masking characters) or `""` (rendering characters in plaintext).

### Q46: What layout managers does Tkinter offer, and which ones did you use?
**Answer:** Tkinter offers three layout managers:
1. `pack()` (flows widgets sequentially).
2. `grid()` (places widgets in a 2D table structure).
3. `place()` (absolute pixel positions).

We used both `grid()` (for structured outer layouts, pages, and sidebars) and `pack()` (for stacking child card widgets and forms), ensuring a fully responsive, proportional screen layout.

### Q47: How did you make the database log viewer list look modern and scrollable?
**Answer:** We styled a `ttk.Treeview` widget with custom column widths, removing default borders, and applying background row configurations. We also linked a vertical `ttk.Scrollbar` to the treeview's `yscrollcommand` properties so the user can scroll through hundreds of logs smoothly.

### Q48: What is the purpose of `self.update_idletasks()` inside progress bar updates?
**Answer:** In Tkinter, redraw events are typically queued to run when the event loop is idle. When executing sequential updates during a thread launch, calling `update_idletasks()` forces Tkinter to immediately redraw pending display widgets (like progress bars and status labels), providing smooth real-time visual progress feedback to the user.

### Q49: What is a Daemon Thread, and why did you configure the background worker threads as daemon?
**Answer:** A daemon thread is a background thread that does not prevent Python from exiting if the main program is closed. By setting `thread.daemon = True` on our file encryption background workers, we ensure that if the user closes the main SecureVault window mid-operation, the background thread is terminated instantly rather than hanging in the task manager.

### Q50: How can this Tkinter desktop application be compiled into a single executable for distribution?
**Answer:** The system can be compiled using **PyInstaller**. By running the command:
`pyinstaller --onefile --windowed --add-data "config;config" --add-data "database;database" main.py`
PyInstaller packages the Python interpreter, our custom code modules, and necessary binary libraries into a single standalone `.exe` file that can be distributed and executed on standard Windows systems without requiring Python to be pre-installed.
