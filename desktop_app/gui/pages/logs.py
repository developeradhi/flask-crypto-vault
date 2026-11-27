"""
System Logs Page Module.
Features structured log trees, query search bounds, level filtering, and db purges.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import THEME
from gui.components import CardFrame, ModernButton, SectionHeader

class LogsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=THEME['bg_main'])
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)  # Toolbar
        self.grid_rowconfigure(2, weight=1)  # Log table
        self.grid_columnconfigure(0, weight=1)
        
        self._build_ui()
        self._load_logs()

    def _build_ui(self):
        # Header title
        header = SectionHeader(self, title="📜 System Activity & Audit Logs")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # 1. Filter Toolbar Frame
        self.toolbar = CardFrame(self, pady=10)
        self.toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Layout weights
        self.toolbar.grid_columnconfigure(0, weight=0)
        self.toolbar.grid_columnconfigure(1, weight=0)
        self.toolbar.grid_columnconfigure(2, weight=0)
        self.toolbar.grid_columnconfigure(3, weight=1)  # Spacer
        self.toolbar.grid_columnconfigure(4, weight=0)
        self.toolbar.grid_columnconfigure(5, weight=0)

        # Filter ComboBox
        lbl_filter = tk.Label(
            self.toolbar, 
            text="Filter Level:", 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_body']
        )
        lbl_filter.grid(row=0, column=0, padx=(5, 10), sticky="w")
        
        self.filter_var = tk.StringVar(value="ALL")
        self.filter_combo = ttk.Combobox(
            self.toolbar, 
            textvariable=self.filter_var, 
            values=["ALL", "INFO", "WARNING", "ERROR"], 
            state="readonly", 
            width=10, 
            font=THEME['font_body']
        )
        self.filter_combo.grid(row=0, column=1, padx=(0, 20), sticky="w")
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self._load_logs())

        # Search Bar
        lbl_search = tk.Label(
            self.toolbar, 
            text="Search:", 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_body']
        )
        lbl_search.grid(row=0, column=2, padx=(0, 10), sticky="w")
        
        self.search_entry = tk.Entry(
            self.toolbar, 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_main'], 
            insertbackground=THEME['accent_primary'], 
            font=THEME['font_body'], 
            highlightbackground=THEME['fg_navbar'], 
            highlightthickness=1, 
            bd=0, 
            width=22
        )
        self.search_entry.grid(row=0, column=3, sticky="w", pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self._load_logs())

        # Action Buttons
        self.refresh_btn = ModernButton(
            self.toolbar, 
            text="🔄 Refresh", 
            command=self._load_logs, 
            bg_color=THEME['accent_secondary'], 
            width=10
        )
        self.refresh_btn.grid(row=0, column=4, padx=5, sticky="e")
        
        self.clear_btn = ModernButton(
            self.toolbar, 
            text="🗑️ Clear DB Logs", 
            command=self._clear_logs, 
            bg_color=THEME['danger'], 
            width=14
        )
        self.clear_btn.grid(row=0, column=5, padx=5, sticky="e")

        # 2. Log Listing Table Frame
        table_card = CardFrame(self)
        table_card.grid(row=2, column=0, sticky="nsew")
        table_card.grid_rowconfigure(0, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        # Custom Styled Treeview
        columns = ("id", "level", "message", "module", "timestamp")
        self.tree = ttk.Treeview(
            table_card, 
            columns=columns, 
            show="headings", 
            style="Custom.Treeview"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Table Headings
        self.tree.heading("id", text="Log ID")
        self.tree.heading("level", text="Severity")
        self.tree.heading("message", text="Audit Log Message Detail")
        self.tree.heading("module", text="Source Module")
        self.tree.heading("timestamp", text="Logged At")

        # Column Layout Widths
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("level", width=100, anchor="center")
        self.tree.column("message", width=480, anchor="w")
        self.tree.column("module", width=140, anchor="w")
        self.tree.column("timestamp", width=160, anchor="center")

        # Scrollbar setup
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Color-coded log severity highlighting
        self.tree.tag_configure("INFO", foreground="#81C784")     # Muted light green
        self.tree.tag_configure("WARNING", foreground="#FFD54F")  # Muted warm yellow
        self.tree.tag_configure("ERROR", foreground="#E57373")    # Muted danger red

    def _load_logs(self):
        """Loads and filters log entries from the database."""
        # Clear existing table items
        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = self.controller.db.get_logs(limit=250)
        filter_level = self.filter_var.get().upper()
        search_query = self.search_entry.get().lower().strip()

        for log in logs:
            level = log['level']
            msg = log['message']
            mod = log['module']
            
            # Filter Level check
            if filter_level != "ALL" and level != filter_level:
                continue
                
            # Filter Search Query check
            if search_query and (search_query not in msg.lower() and search_query not in mod.lower()):
                continue

            self.tree.insert(
                "", 
                "end", 
                values=(
                    f"#{log['id']}", 
                    level, 
                    msg, 
                    mod, 
                    log['timestamp']
                ),
                tags=(level,)
            )

    def _clear_logs(self):
        """Purges local event storage tables on confirmation."""
        if messagebox.askyesno("Confirm Purge", "Are you sure you want to permanently clear all database system logs?"):
            self.controller.db.clear_logs()
            self._load_logs()
            messagebox.showinfo("Purged", "Database system activity log has been cleared.")
