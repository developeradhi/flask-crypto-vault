"""
Encrypt Page Module.
Provides file encryption selectors, password derivations, and visual progress states.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import threading
from pathlib import Path
from config.settings import THEME, ENCRYPTED_DIR
from gui.components import CardFrame, ModernButton, InputField, SecureInputField, SectionHeader
from security.encryptor import SecureEncryptor

class EncryptPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME['bg_main'])
        self.controller = controller
        
        self.selected_file_path = None
        self.selected_dest_dir = str(ENCRYPTED_DIR)
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._build_ui()

    def _build_ui(self):
        # Header title
        header = SectionHeader(self, title="🔒 Secure File Encryption")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Central card container
        self.card = CardFrame(self)
        self.card.grid(row=1, column=0, sticky="nsew")
        
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_columnconfigure(1, weight=1)
        
        # LEFT COLUMN - File Selection Details
        left_pane = tk.Frame(self.card, bg=THEME['bg_card'])
        left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)
        left_pane.grid_columnconfigure(0, weight=1)
        
        lbl_step1 = tk.Label(
            left_pane, 
            text="1️⃣ Select Target File", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h2'], 
            anchor="w"
        )
        lbl_step1.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # File selector input bar
        self.file_input = InputField(left_pane, label_text="Choose file to encrypt securely:")
        self.file_input.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.file_input.entry.config(state="readonly")
        
        self.browse_file_btn = ModernButton(
            left_pane, 
            text="📁 Browse File", 
            command=self._browse_file, 
            bg_color=THEME['accent_secondary']
        )
        self.browse_file_btn.grid(row=2, column=0, sticky="w", pady=(0, 20))
        
        # Selected File Metadata Inspector
        self.meta_frame = tk.LabelFrame(
            left_pane, 
            text="🔍 Selected File Metadata Info", 
            bg=THEME['bg_card'], 
            fg=THEME['fg_primary'], 
            font=THEME['font_body'], 
            bd=1, 
            highlightthickness=0, 
            relief="solid", 
            padx=10, 
            pady=10
        )
        self.meta_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        self.lbl_meta_name = tk.Label(self.meta_frame, text="Name: N/A", fg=THEME['fg_secondary'], bg=THEME['bg_card'], font=THEME['font_small'], anchor="w")
        self.lbl_meta_name.pack(fill="x")
        self.lbl_meta_size = tk.Label(self.meta_frame, text="Size: N/A", fg=THEME['fg_secondary'], bg=THEME['bg_card'], font=THEME['font_small'], anchor="w")
        self.lbl_meta_size.pack(fill="x")
        self.lbl_meta_type = tk.Label(self.meta_frame, text="Format Type: N/A", fg=THEME['fg_secondary'], bg=THEME['bg_card'], font=THEME['font_small'], anchor="w")
        self.lbl_meta_type.pack(fill="x")

        # Destination selector
        lbl_dest = tk.Label(
            left_pane, 
            text="📍 Destination Directory", 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_body'], 
            anchor="w"
        )
        lbl_dest.grid(row=4, column=0, sticky="w", pady=(10, 5))
        
        self.dest_input = InputField(left_pane, label_text="")
        self.dest_input.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        self.dest_input.set(self.selected_dest_dir)
        self.dest_input.entry.config(state="readonly")
        
        self.browse_dest_btn = ModernButton(
            left_pane, 
            text="🗺️ Change Folder", 
            command=self._browse_dest, 
            bg_color=THEME['bg_hover']
        )
        self.browse_dest_btn.grid(row=6, column=0, sticky="w")

        # RIGHT COLUMN - Password Constraints & Execution
        right_pane = tk.Frame(self.card, bg=THEME['bg_card'])
        right_pane.grid(row=0, column=1, sticky="nsew", padx=(20, 0), pady=10)
        right_pane.grid_columnconfigure(0, weight=1)
        
        lbl_step2 = tk.Label(
            right_pane, 
            text="2️⃣ Authentication Password", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h2'], 
            anchor="w"
        )
        lbl_step2.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.pwd_input = SecureInputField(right_pane, label_text="Create session encryption password:")
        self.pwd_input.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        self.confirm_pwd_input = SecureInputField(right_pane, label_text="Verify session password:")
        self.confirm_pwd_input.grid(row=2, column=0, sticky="ew", pady=(0, 25))

        # Action Execution Frame
        self.exec_frame = tk.Frame(right_pane, bg=THEME['bg_card'])
        self.exec_frame.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        self.exec_frame.grid_columnconfigure(0, weight=1)
        
        self.encrypt_action_btn = ModernButton(
            self.exec_frame, 
            text="🔒 Begin Secure Encryption", 
            command=self._handle_encryption, 
            bg_color=THEME['accent_primary'], 
            width=30
        )
        self.encrypt_action_btn.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Progress Bar indicators
        self.progress_lbl = tk.Label(
            self.exec_frame, 
            text="System Idle...", 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_small']
        )
        self.progress_lbl.grid(row=1, column=0, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.exec_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=2, column=0, sticky="ew")

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Any File for Encryption",
            filetypes=[("All Files", "*.*")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_input.entry.config(state="normal")
            self.file_input.set(file_path)
            self.file_input.entry.config(state="readonly")
            
            # Extract metadata details
            name = os.path.basename(file_path)
            size_bytes = os.path.getsize(file_path)
            suffix = Path(file_path).suffix.upper().replace(".", "") or "Binary"
            
            self.lbl_meta_name.config(text=f"Name: {name}")
            self.lbl_meta_size.config(text=f"Size: {self._format_size(size_bytes)}")
            self.lbl_meta_type.config(text=f"Format Type: {suffix} File")

    def _browse_dest(self):
        folder = filedialog.askdirectory(title="Choose Output Encrypted Files Directory")
        if folder:
            self.selected_dest_dir = folder
            self.dest_input.entry.config(state="normal")
            self.dest_input.set(folder)
            self.dest_input.entry.config(state="readonly")

    def _handle_encryption(self):
        # 1. Validation
        if not self.selected_file_path:
            messagebox.showerror("Validation Error", "Please select a file to encrypt.")
            return
            
        password = self.pwd_input.get()
        confirm = self.confirm_pwd_input.get()
        
        if not password or not confirm:
            messagebox.showerror("Validation Error", "Please fill in all credentials inputs.")
            return
            
        if password != confirm:
            messagebox.showerror("Validation Error", "Session passwords do not match.")
            return

        if len(password) < 6:
            messagebox.showerror("Weak Password", "Session password must be at least 6 characters.")
            return

        # 2. Lock UI buttons to prevent parallel triggers
        self.encrypt_action_btn.configure_state("disabled")
        self.browse_file_btn.configure_state("disabled")
        self.browse_dest_btn.configure_state("disabled")
        self.progress_lbl.config(text="Processing PBKDF2 Key Derivation...", fg=THEME['accent_primary'])
        self.progress_bar.config(value=10)
        
        # Use simple background thread for smooth UI responsiveness
        thread = threading.Thread(target=self._run_encryption_thread, args=(password,))
        thread.daemon = True
        thread.start()

    def _run_encryption_thread(self, password):
        try:
            time.sleep(0.5)  # Visual micro-delay for animation smooth flow
            self._update_progress("Hashing file structure...", 40)
            
            # Derive output path
            basename = os.path.basename(self.selected_file_path)
            output_name = basename + ".enc"
            output_path = os.path.join(self.selected_dest_dir, output_name)
            
            # Run secure encryptor core library
            output_path, size_bytes, encrypted_hash, salt_hex = SecureEncryptor.encrypt_file(
                self.selected_file_path,
                password,
                output_path
            )
            
            self._update_progress("Finalizing SQLite catalog logging...", 80)
            time.sleep(0.3)
            
            # Log in database
            user_id = self.controller.current_user['id'] if self.controller.current_user else None
            self.controller.db.add_history_entry(
                user_id=user_id,
                action_type="ENCRYPT",
                original_filename=basename,
                processed_filename=os.path.basename(output_path),
                file_size=size_bytes,
                file_hash=encrypted_hash
            )
            self.controller.db.log_event(
                "INFO", 
                f"Successfully encrypted file '{basename}' to output file '{os.path.basename(output_path)}'. Size: {size_bytes}B", 
                "EncryptPage"
            )
            
            self._update_progress("Encryption Complete!", 100)
            messagebox.showinfo("Success", f"File Encrypted Successfully!\nSaved to: {output_path}")
            
            # Reset UI inputs on success
            self._reset_ui()
            
        except Exception as e:
            self.controller.db.log_event("ERROR", f"File encryption operation failed: {str(e)}", "EncryptPage")
            self._update_progress("Operation Failed!", 0, THEME['danger'])
            messagebox.showerror("Runtime Cryptography Failure", f"An error occurred during encryption: {str(e)}")
            self._unlock_ui()

    def _update_progress(self, text, val, color=THEME['accent_primary']):
        self.progress_lbl.config(text=text, fg=color)
        self.progress_bar.config(value=val)
        self.update_idletasks()

    def _reset_ui(self):
        self.selected_file_path = None
        self.file_input.entry.config(state="normal")
        self.file_input.clear()
        self.file_input.entry.config(state="readonly")
        
        self.pwd_input.clear()
        self.confirm_pwd_input.clear()
        
        self.lbl_meta_name.config(text="Name: N/A")
        self.lbl_meta_size.config(text="Size: N/A")
        self.lbl_meta_type.config(text="Format Type: N/A")
        
        self.progress_lbl.config(text="System Idle...", fg=THEME['fg_secondary'])
        self.progress_bar.config(value=0)
        self._unlock_ui()

    def _unlock_ui(self):
        self.encrypt_action_btn.configure_state("normal")
        self.browse_file_btn.configure_state("normal")
        self.browse_dest_btn.configure_state("normal")

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
