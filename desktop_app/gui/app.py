"""
GUI Application Master Module.
Coordinates page routing, session state, and layout geometry.
"""
import tkinter as tk
from tkinter import messagebox
from config.settings import THEME
from database.manager import DatabaseManager

class SecureVaultApp(tk.Tk):
    def __init__(self, db_manager=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Secure File Encryption & Decryption System")
        self.geometry("1100x700")
        self.minsize(950, 600)
        self.configure(bg=THEME['bg_main'])
        
        # Core data layers
        self.db = db_manager or DatabaseManager()
        self.current_user = None  # Holds dict of currently authenticated user: {'id': 1, 'username': 'admin'}
        
        # Primary container configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Navbar column
        self.grid_columnconfigure(1, weight=1)  # Main Content column

        # Initialize core structure layout
        self.navbar_frame = None
        self.content_container = tk.Frame(self, bg=THEME['bg_main'])
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        # Registered Pages mapping
        self.frames = {}
        self.active_frame_class = None
        
        # Display initial page (Authentication Page)
        self.show_auth_page()

    def show_auth_page(self):
        """Hides internal navigation and forces login screen."""
        self.current_user = None
        if self.navbar_frame:
            self.navbar_frame.grid_forget()
            self.navbar_frame = None
            
        # Reconfigure grid to make login full screen
        self.grid_columnconfigure(0, weight=1)
        self.content_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Load Login Page
        from gui.pages.login import LoginPage
        self._switch_to_frame(LoginPage)

    def login_user(self, user_dict):
        """Sets active user credentials session and renders dashboard."""
        self.current_user = user_dict
        self.db.log_event("INFO", f"User '{user_dict['username']}' authenticated successfully.", "SessionManager")
        
        # Restore two-column navbar layout
        self.content_container.grid_forget()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Create persistent navigation bar
        self._build_navigation_bar()
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        
        # Render Dashboard
        from gui.pages.dashboard import DashboardPage
        self.show_page(DashboardPage)

    def logout_user(self):
        """Terminates session and returns to login screen."""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of SecureVault?"):
            username = self.current_user['username'] if self.current_user else "unknown"
            self.db.log_event("INFO", f"User '{username}' logged out.", "SessionManager")
            self.show_auth_page()

    def _build_navigation_bar(self):
        """Creates the premium side navigation panel."""
        self.navbar_frame = tk.Frame(self, bg=THEME['bg_navbar'], width=220, highlightthickness=0)
        self.navbar_frame.grid(row=0, column=0, sticky="nsew")
        self.navbar_frame.grid_propagate(False)

        # Header Title
        logo_lbl = tk.Label(
            self.navbar_frame, 
            text="🛡️ SecureVault", 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_navbar'], 
            font=THEME['font_h2']
        )
        logo_lbl.pack(fill="x", pady=25)

        # Separator line
        sep = tk.Frame(self.navbar_frame, bg=THEME['bg_hover'], height=1)
        sep.pack(fill="x", padx=15, pady=(0, 20))

        # Nav Buttons mapping
        from gui.pages.dashboard import DashboardPage
        from gui.pages.encrypt import EncryptPage
        from gui.pages.decrypt import DecryptPage
        from gui.pages.logs import LogsPage
        from gui.pages.settings import SettingsPage
        from gui.pages.about import AboutPage

        menu_items = [
            ("📊 Dashboard", DashboardPage),
            ("🔒 Encrypt File", EncryptPage),
            ("🔓 Decrypt File", DecryptPage),
            ("📜 System Logs", LogsPage),
            ("⚙️ Settings", SettingsPage),
            ("ℹ️ About System", AboutPage),
        ]

        self.nav_buttons = {}
        for text, page_cls in menu_items:
            btn = tk.Label(
                self.navbar_frame, 
                text=text, 
                fg=THEME['fg_navbar'], 
                bg=THEME['bg_navbar'], 
                font=THEME['font_body'], 
                anchor="w", 
                padx=20, 
                pady=12, 
                cursor="hand2"
            )
            btn.pack(fill="x")
            
            # Hover animations and routing actions
            btn.bind("<Enter>", lambda e, b=btn: self._on_nav_enter(b))
            btn.bind("<Leave>", lambda e, b=btn, p=page_cls: self._on_nav_leave(b, p))
            btn.bind("<Button-1>", lambda e, p=page_cls: self.show_page(p))
            
            self.nav_buttons[page_cls] = btn

        # Logout Button anchored to the bottom
        logout_btn = tk.Label(
            self.navbar_frame, 
            text="🚪 Logout Session", 
            fg=THEME['danger'], 
            bg=THEME['bg_navbar'], 
            font=THEME['font_body'], 
            anchor="w", 
            padx=20, 
            pady=15, 
            cursor="hand2"
        )
        logout_btn.pack(side="bottom", fill="x", pady=15)
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg=THEME['bg_hover']))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg=THEME['bg_navbar']))
        logout_btn.bind("<Button-1>", lambda e: self.logout_user())

    def _on_nav_enter(self, label):
        label.config(bg=THEME['bg_hover'], fg=THEME['fg_primary'])

    def _on_nav_leave(self, label, page_cls):
        if self.active_frame_class != page_cls:
            label.config(bg=THEME['bg_navbar'], fg=THEME['fg_navbar'])
        else:
            label.config(bg=THEME['bg_hover'], fg=THEME['accent_primary'])

    def show_page(self, page_class):
        """Switches visible content and highlights selected navigation item."""
        self.active_frame_class = page_class
        
        # Update navigation menu styling highlight
        if self.navbar_frame:
            for cls, btn in self.nav_buttons.items():
                if cls == page_class:
                    btn.config(bg=THEME['bg_hover'], fg=THEME['accent_primary'])
                else:
                    btn.config(bg=THEME['bg_navbar'], fg=THEME['fg_navbar'])
                    
        self._switch_to_frame(page_class)

    def _switch_to_frame(self, page_class):
        """Destroys and recreates target page context dynamically."""
        if page_class in self.frames:
            self.frames[page_class].destroy()
            
        frame = page_class(self.content_container, self)
        self.frames[page_class] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        
        # Ensure focus is initialized properly
        frame.focus_set()
