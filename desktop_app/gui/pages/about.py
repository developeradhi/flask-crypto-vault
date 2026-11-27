"""
About Page Module.
Provides academic documentation of the security architectures, modules, and algorithm parameters.
"""
import tkinter as tk
from config.settings import THEME
from gui.components import CardFrame, SectionHeader

class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME['bg_main'])
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._build_ui()

    def _build_ui(self):
        # Header title
        header = SectionHeader(self, title="ℹ️ About Security & Architecture")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Central card container
        self.card = CardFrame(self)
        self.card.grid(row=1, column=0, sticky="nsew")
        self.card.pack_propagate(False)

        # Scrollable container for a lot of details
        canvas = tk.Canvas(self.card, bg=THEME['bg_card'], highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.card, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME['bg_card'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # System title inside panel
        title_lbl = tk.Label(
            scrollable_frame, 
            text="🛡️ Secure File Encryption and Decryption System v1.0.0", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h2'], 
            anchor="w"
        )
        title_lbl.pack(fill="x", pady=(0, 15))

        desc_lbl = tk.Label(
            scrollable_frame, 
            text="This academic software project provides state-of-the-art protection for individual and multi-format files using industry-standard cryptography models. Below is an educational breakdown of the underlying security primitives implemented in this application.", 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_body'], 
            wraplength=640, 
            justify="left"
        )
        desc_lbl.pack(fill="x", pady=(0, 25))

        # Core Primitives
        primitives = [
            ("1. Advanced Encryption Standard (AES)", 
             "AES-256 standard encryption operates under a symmetric block cipher design. Through our adoption of the Fernet standard framework, the payload is protected using AES in Cipher Block Chaining (CBC) mode with a 128-bit key. It guarantees that an adversary cannot read or modify the encrypted files without possessing the correct session key."),
            
            ("2. Key Derivation Function (PBKDF2-HMAC-SHA256)", 
             "Direct passwords are vulnerable to dictionary attacks. SecureVault uses Password-Based Key Derivation Function 2 (PBKDF2) combined with a cryptographically secure 16-byte salt and 100,000 iterations of SHA-256. This derives a unique 32-byte key compliant with Fernet constraints, slowing down dictionary and hardware brute-force attacks significantly."),
            
            ("3. Cryptographic Salt Generation", 
             "Each file encryption process generates a unique, random 16-byte salt via os.urandom(). The salt is stored in the header of the .enc file (first 16 bytes). Because salt is unique for every operation, identical files encrypted with the same password produce completely distinct ciphertexts, rendering rainbow-table attacks useless."),
            
            ("4. Local User Authentication (SHA-256 with Salt)", 
             "Local sign-in credentials are never stored in plain text inside SQLite databases. When registering, SecureVault generates a 16-byte random salt and computes a SHA-256 hex signature: Hex(SHA256(Salt || Password)). On login, the user's password input is salted and hashed using the stored salt to verify the signature, protecting user credentials in the event of database exposure."),
            
            ("5. Integrity Verification (HMAC & SHA-256 Checksums)", 
             "Fernet standard envelope structures inherently use HMAC-SHA256 authentication signatures. When decrypting a file, Fernet verifies that the ciphertext and header have not been tampered with. Additionally, the system hashes files before and after operations, logging SHA-256 file checksums into the database to assert full operational audit matching.")
        ]

        for heading, body in primitives:
            # Section Card Frame
            f = tk.Frame(scrollable_frame, bg=THEME['bg_card'])
            f.pack(fill="x", pady=(0, 20))
            
            lbl_head = tk.Label(
                f, 
                text=heading, 
                fg=THEME['accent_secondary'], 
                bg=THEME['bg_card'], 
                font=THEME['font_h2'], 
                anchor="w"
            )
            lbl_head.pack(fill="x", pady=(0, 5))
            
            lbl_body = tk.Label(
                f, 
                text=body, 
                fg=THEME['fg_secondary'], 
                bg=THEME['bg_card'], 
                font=THEME['font_small'], 
                wraplength=640, 
                justify="left"
            )
            lbl_body.pack(fill="x")
