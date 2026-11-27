"""
Dashboard Page Module.
Presents session metrics, aggregate stats, and recent history logs.
"""
import tkinter as tk
from tkinter import ttk
from config.settings import THEME
from gui.components import CardFrame, ModernButton, SectionHeader

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME['bg_main'])
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Stats cards
        self.grid_rowconfigure(2, weight=1)  # History list table
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self._build_ui()

    def _build_ui(self):
        # 1. Header Layout
        username = self.controller.current_user['username'].capitalize() if self.controller.current_user else "User"
        header = SectionHeader(self, title=f"📊 Welcome Back, {username}")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        # Load user history stats
        history = []
        if self.controller.current_user:
            history = self.controller.db.get_user_history(self.controller.current_user['id'])
            
        enc_count = sum(1 for item in history if item['action_type'] == 'ENCRYPT')
        dec_count = sum(1 for item in history if item['action_type'] == 'DECRYPT')
        total_ops = len(history)

        # 2. Statistics Card Frames
        # Card A: Encrypted Files
        card_a = CardFrame(self)
        card_a.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 20))
        self._setup_stat_card(card_a, "🔒 Encrypted Files", enc_count, THEME['accent_primary'])

        # Card B: Decrypted Files
        card_b = CardFrame(self)
        card_b.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 20))
        self._setup_stat_card(card_b, "🔓 Decrypted Files", dec_count, THEME['accent_secondary'])

        # Card C: Total Tasks
        card_c = CardFrame(self)
        card_c.grid(row=1, column=2, sticky="nsew", padx=(10, 0), pady=(0, 20))
        self._setup_stat_card(card_c, "🔄 Total Operations", total_ops, THEME['success'])

        # 3. Recent Activity Section
        list_card = CardFrame(self)
        list_card.grid(row=2, column=0, columnspan=3, sticky="nsew")
        list_card.grid_rowconfigure(0, weight=0)
        list_card.grid_rowconfigure(1, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        list_title = tk.Label(
            list_card, 
            text="⏳ Recent Cryptographic History", 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_h2'], 
            anchor="w"
        )
        list_title.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Styled Table Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Treeview",
            background=THEME['bg_card'],
            foreground=THEME['fg_primary'],
            fieldbackground=THEME['bg_card'],
            rowheight=30,
            borderwidth=0,
            font=THEME['font_body']
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=THEME['bg_navbar'],
            foreground=THEME['accent_primary'],
            font=THEME['font_h2'],
            borderwidth=0
        )
        style.map("Custom.Treeview", background=[("selected", THEME['bg_hover'])])

        # Define Columns
        columns = ("id", "type", "orig_file", "proc_file", "size", "timestamp")
        self.tree = ttk.Treeview(
            list_card, 
            columns=columns, 
            show="headings", 
            style="Custom.Treeview"
        )
        self.tree.grid(row=1, column=0, sticky="nsew")

        # Headings Setup
        self.tree.heading("id", text="Op ID")
        self.tree.heading("type", text="Action")
        self.tree.heading("orig_file", text="Original File")
        self.tree.heading("proc_file", text="Output File")
        self.tree.heading("size", text="File Size")
        self.tree.heading("timestamp", text="Executed At")

        # Column Layout Widths
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("orig_file", width=240, anchor="w")
        self.tree.column("proc_file", width=240, anchor="w")
        self.tree.column("size", width=100, anchor="e")
        self.tree.column("timestamp", width=160, anchor="center")

        # Scrollbar setup
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Populating historical entries
        for row_data in history[:8]:  # Limit dashboard display list to top 8 entries
            size_formatted = self._format_size(row_data['file_size'])
            action_icon = "🔒 ENCRYPT" if row_data['action_type'] == 'ENCRYPT' else "🔓 DECRYPT"
            
            self.tree.insert(
                "", 
                "end", 
                values=(
                    f"#{row_data['id']}", 
                    action_icon, 
                    row_data['original_filename'], 
                    row_data['processed_filename'], 
                    size_formatted, 
                    row_data['timestamp']
                )
            )

    def _setup_stat_card(self, card, title, val, accent_color):
        card.grid_columnconfigure(0, weight=1)
        
        lbl_title = tk.Label(
            card, 
            text=title, 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_body'], 
            anchor="w"
        )
        lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        lbl_val = tk.Label(
            card, 
            text=str(val), 
            fg=accent_color, 
            bg=THEME['bg_card'], 
            font=("Segoe UI", 36, "bold"), 
            anchor="w"
        )
        lbl_val.grid(row=1, column=0, sticky="w")

    def _format_size(self, size_bytes):
        """Converts raw byte sizes to standard readable metrics."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
