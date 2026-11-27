"""
Login and Registration Page.
Implements authentication flows and handles credential validation.
"""
import tkinter as tk
from tkinter import messagebox
from config.settings import THEME
from gui.components import CardFrame, ModernButton, InputField, SecureInputField
from security.encryptor import SecureEncryptor

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME['bg_main'])
        self.controller = controller
        
        # Center column container
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        
        self.is_register_mode = False
        self._build_ui()

    def _build_ui(self):
        # Card Container
        self.card = CardFrame(self, width=420, height=520)
        self.card.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.card.pack_propagate(False)
        
        # Title Header
        self.title_lbl = tk.Label(
            self.card, 
            text="🔒 SecureVault Login", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h1']
        )
        self.title_lbl.pack(pady=(30, 20))
        
        self.subtitle_lbl = tk.Label(
            self.card, 
            text="Please authenticate to access encrypted storage.", 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_body'], 
            wraplength=350
        )
        self.subtitle_lbl.pack(pady=(0, 25))

        # Username Input
        self.username_input = InputField(self.card, label_text="Username")
        self.username_input.pack(fill="x", padx=30, pady=(0, 15))
        
        # Password Input
        self.password_input = SecureInputField(self.card, label_text="Master Password")
        self.password_input.pack(fill="x", padx=30, pady=(0, 15))
        
        # Confirm Password Input (Hidden initially)
        self.confirm_password_input = SecureInputField(self.card, label_text="Confirm Password")

        # Dynamic Action Buttons Frame
        self.btn_frame = tk.Frame(self.card, bg=THEME['bg_card'])
        self.btn_frame.pack(fill="x", padx=30, pady=10)
        
        self.action_btn = ModernButton(
            self.btn_frame, 
            text="Sign In", 
            command=self._handle_action, 
            width=28
        )
        self.action_btn.pack(fill="x", pady=10)
        
        self.toggle_mode_lbl = tk.Label(
            self.card, 
            text="Don't have a secure vault? Register Now", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_small'], 
            cursor="hand2"
        )
        self.toggle_mode_lbl.pack(pady=10)
        self.toggle_mode_lbl.bind("<Button-1>", self._toggle_mode)

    def _toggle_mode(self, event=None):
        self.is_register_mode = not self.is_register_mode
        
        # Clear fields
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        
        if self.is_register_mode:
            self.title_lbl.config(text="🆕 Register Vault")
            self.subtitle_lbl.config(text="Create a secure master login credentials profile.")
            
            # Show Confirm Password
            self.confirm_password_input.pack(fill="x", padx=30, pady=(0, 15), before=self.btn_frame)
            self.action_btn.label.config(text="Create Vault")
            self.toggle_mode_lbl.config(text="Already registered? Sign In here")
            self.card.config(height=580)
        else:
            self.title_lbl.config(text="🔒 SecureVault Login")
            self.subtitle_lbl.config(text="Please authenticate to access encrypted storage.")
            
            # Hide Confirm Password
            self.confirm_password_input.pack_forget()
            self.action_btn.label.config(text="Sign In")
            self.toggle_mode_lbl.config(text="Don't have a secure vault? Register Now")
            self.card.config(height=520)

    def _handle_action(self):
        username = self.username_input.get().strip()
        password = self.password_input.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all security fields.")
            return

        if len(password) < 6:
            messagebox.showerror("Security Warning", "Master password must be at least 6 characters long.")
            return

        if self.is_register_mode:
            confirm = self.confirm_password_input.get()
            if password != confirm:
                messagebox.showerror("Registration Error", "Passwords do not match.")
                return
            
            try:
                # Hash the master password with a cryptographically secure salt
                password_hash, salt = SecureEncryptor.hash_password(password)
                
                # Insert into the database
                self.controller.db.register_user(username, password_hash, salt)
                self.controller.db.log_event("INFO", f"Registered new user '{username}'.", "Authentication")
                
                messagebox.showinfo("Vault Created", "Your SecureVault has been initialized! Please sign in now.")
                self._toggle_mode()
            except ValueError as val_err:
                messagebox.showerror("Unique Constraint", str(val_err))
            except Exception as e:
                messagebox.showerror("Database Failure", f"An unexpected database error occurred: {str(e)}")
        else:
            # Login authentication flow
            user = self.controller.db.get_user(username)
            if not user:
                self.controller.db.log_event("WARNING", f"Failed authentication attempt for non-existent user '{username}'", "Authentication")
                messagebox.showerror("Access Denied", "Invalid username or password combination.")
                return
            
            # Validate hash
            is_valid = SecureEncryptor.verify_password(password, user['password_hash'], user['salt'])
            if is_valid:
                # Store user session dict
                session_dict = {
                    'id': user['id'],
                    'username': user['username']
                }
                self.controller.login_user(session_dict)
            else:
                self.controller.db.log_event("WARNING", f"Invalid password attempt for user '{username}'", "Authentication")
                messagebox.showerror("Access Denied", "Invalid username or password combination.")
