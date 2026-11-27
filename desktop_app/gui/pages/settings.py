"""
Settings Page Module.
Provides secure password updates, database metrics inspection, and cleanup options.
"""
import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path
from config.settings import THEME, DB_PATH
from gui.components import CardFrame, ModernButton, SecureInputField, SectionHeader
from security.encryptor import SecureEncryptor

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME['bg_main'])
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self._build_ui()

    def _build_ui(self):
        # Header title
        header = SectionHeader(self, title="⚙️ Application & Security Settings")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # LEFT COLUMN - Account Password Change
        left_card = CardFrame(self)
        left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_card.grid_columnconfigure(0, weight=1)
        
        lbl_acc = tk.Label(
            left_card, 
            text="👤 Update Master credentials", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h2'], 
            anchor="w"
        )
        lbl_acc.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.old_pwd_input = SecureInputField(left_card, label_text="Current Master Password:")
        self.old_pwd_input.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.new_pwd_input = SecureInputField(left_card, label_text="New Master Password:")
        self.new_pwd_input.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.confirm_new_pwd_input = SecureInputField(left_card, label_text="Confirm New Password:")
        self.confirm_new_pwd_input.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        self.save_pwd_btn = ModernButton(
            left_card, 
            text="💾 Save Password", 
            command=self._change_password, 
            width=20
        )
        self.save_pwd_btn.grid(row=4, column=0, sticky="w")

        # RIGHT COLUMN - Vault Database Stats & Reset Tooling
        right_card = CardFrame(self)
        right_card.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right_card.grid_columnconfigure(0, weight=1)
        
        lbl_db = tk.Label(
            right_card, 
            text="🗄️ Database & Security Storage", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h2'], 
            anchor="w"
        )
        lbl_db.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # DB Statistics Frame
        stats_frame = tk.Frame(right_card, bg=THEME['bg_card'], highlightthickness=0)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Calculate sqlite database values
        db_size_bytes = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        db_history_cnt = 0
        if self.controller.current_user:
            db_history_cnt = len(self.controller.db.get_user_history(self.controller.current_user['id']))
            
        self.lbl_db_path = tk.Label(
            stats_frame, 
            text=f"Location: {DB_PATH}", 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_small'], 
            anchor="w", 
            wraplength=400
        )
        self.lbl_db_path.pack(fill="x", pady=2)
        
        self.lbl_db_size = tk.Label(
            stats_frame, 
            text=f"Database File Size: {db_size_bytes / 1024:.2f} KB", 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_small'], 
            anchor="w"
        )
        self.lbl_db_size.pack(fill="x", pady=2)
        
        self.lbl_history_cnt = tk.Label(
            stats_frame, 
            text=f"Your Logged Operations: {db_history_cnt} records", 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_small'], 
            anchor="w"
        )
        self.lbl_history_cnt.pack(fill="x", pady=2)

        # Danger Zone Cleanups
        lbl_danger = tk.Label(
            right_card, 
            text="⚠️ Danger Zone Utility", 
            fg=THEME['danger'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h2'], 
            anchor="w"
        )
        lbl_danger.grid(row=2, column=0, sticky="w", pady=(10, 10))
        
        lbl_danger_info = tk.Label(
            right_card, 
            text="The actions below are destructive. Purging logs or resetting historical catalogs cannot be undone.", 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_small'], 
            justify="left", 
            wraplength=400
        )
        lbl_danger_info.grid(row=3, column=0, sticky="w", pady=(0, 15))
        
        self.reset_history_btn = ModernButton(
            right_card, 
            text="💥 Reset Encryption History", 
            command=self._reset_history, 
            bg_color=THEME['danger'], 
            width=25
        )
        self.reset_history_btn.grid(row=4, column=0, sticky="w")

    def _change_password(self):
        old_pwd = self.old_pwd_input.get()
        new_pwd = self.new_pwd_input.get()
        confirm = self.confirm_new_pwd_input.get()
        
        if not old_pwd or not new_pwd or not confirm:
            messagebox.showerror("Error", "Please fill in all security input fields.")
            return

        if len(new_pwd) < 6:
            messagebox.showerror("Validation Error", "New master password must be at least 6 characters.")
            return

        if new_pwd != confirm:
            messagebox.showerror("Validation Error", "New passwords do not match.")
            return

        # Fetch current user credentials
        username = self.controller.current_user['username']
        user = self.controller.db.get_user(username)
        
        if not user:
            messagebox.showerror("Failure", "Failed to retrieve user session details.")
            return
            
        # Verify old password
        is_valid = SecureEncryptor.verify_password(old_pwd, user['password_hash'], user['salt'])
        if not is_valid:
            messagebox.showerror("Access Denied", "Current master password entered is incorrect.")
            return
            
        # Update user with new hashed credentials
        try:
            new_hash, new_salt = SecureEncryptor.hash_password(new_pwd)
            
            with self.controller.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Users SET password_hash = ?, salt = ? WHERE id = ?",
                    (new_hash, new_salt, user['id'])
                )
                conn.commit()
                
            self.controller.db.log_event("INFO", f"User '{username}' modified master password profile.", "SettingsPage")
            messagebox.showinfo("Success", "Master security credentials updated successfully!")
            
            # Clear fields
            self.old_pwd_input.clear()
            self.new_pwd_input.clear()
            self.confirm_new_pwd_input.clear()
        except Exception as e:
            self.controller.db.log_event("ERROR", f"Failed updating credentials database: {str(e)}", "SettingsPage")
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    def _reset_history(self):
        if not self.controller.current_user:
            return
            
        if messagebox.askyesno("Confirm History Purge", "Confirming will delete your local encryption and decryption activity catalogs. Proceed?"):
            try:
                user_id = self.controller.current_user['id']
                with self.controller.db._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM EncryptionHistory WHERE user_id = ?", (user_id,))
                    conn.commit()
                    
                self.controller.db.log_event("INFO", "User deleted local file operations history catalog.", "SettingsPage")
                messagebox.showinfo("Reset Successful", "Your local operations history has been wiped.")
                
                # Refresh metrics labels
                db_size_bytes = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
                self.lbl_db_size.config(text=f"Database File Size: {db_size_bytes / 1024:.2f} KB")
                self.lbl_history_cnt.config(text="Your Logged Operations: 0 records")
            except Exception as e:
                self.controller.db.log_event("ERROR", f"Failed clearing history databases: {str(e)}", "SettingsPage")
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
