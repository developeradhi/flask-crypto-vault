"""
GUI Components Module.
Defines premium custom Tkinter widgets (cards, hover buttons, inputs, secure password toggles)
adhering to the theme guidelines.
"""
import tkinter as tk
from tkinter import ttk
from config.settings import THEME

class CardFrame(tk.Frame):
    """
    A custom card container with a modern thin border and dark card background.
    """
    def __init__(self, master, **kwargs):
        bg_color = kwargs.pop('bg', THEME['bg_card'])
        padx = kwargs.pop('padx', 15)
        pady = kwargs.pop('pady', 15)
        
        super().__init__(
            master, 
            bg=bg_color, 
            highlightbackground=THEME['accent_secondary'], 
            highlightthickness=1, 
            bd=0, 
            **kwargs
        )
        self.pack_propagate(True)
        self.grid_propagate(True)

class ModernButton(tk.Frame):
    """
    Custom hover-enabled flat button with smooth color transition states.
    """
    def __init__(self, master, text, command, bg_color=THEME['accent_primary'], 
                 fg_color="#FFFFFF", hover_bg=None, font=THEME['font_body'], 
                 width=15, height=1, **kwargs):
        super().__init__(master, bg=bg_color, bd=0, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        # Calculate hover background color automatically if not specified
        if hover_bg is None:
            # Simple color shifting towards lighter state
            self.hover_bg = THEME['accent_secondary']
        else:
            self.hover_bg = hover_bg

        self.label = tk.Label(
            self, 
            text=text, 
            fg=fg_color, 
            bg=bg_color, 
            font=font, 
            width=width, 
            height=height, 
            cursor="hand2"
        )
        self.label.pack(fill="both", expand=True, padx=10, pady=5)

        # Bind event triggers for visual interactivity
        self.label.bind("<Button-1>", self._on_click)
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.config(bg=self.hover_bg)
        self.label.config(bg=self.hover_bg)

    def _on_leave(self, event):
        self.config(bg=self.bg_color)
        self.label.config(bg=self.bg_color)

    def configure_state(self, state):
        """Enable or disable button."""
        if state == "disabled":
            self.label.config(state="disabled", fg=THEME['fg_secondary'], cursor="arrow")
            self.label.unbind("<Button-1>")
            self.label.unbind("<Enter>")
            self.label.unbind("<Leave>")
        else:
            self.label.config(state="normal", fg=self.fg_color, cursor="hand2")
            self.label.bind("<Button-1>", self._on_click)
            self.label.bind("<Enter>", self._on_enter)
            self.label.bind("<Leave>", self._on_leave)

class InputField(tk.Frame):
    """
    Standard dark-themed input text field with custom labels.
    """
    def __init__(self, master, label_text, show=None, **kwargs):
        super().__init__(master, bg=THEME['bg_card'], **kwargs)
        
        self.label = tk.Label(
            self, 
            text=label_text, 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_card'], 
            font=THEME['font_body'], 
            anchor="w"
        )
        self.label.pack(fill="x", pady=(0, 5))
        
        # Styled entry container
        self.entry_frame = tk.Frame(
            self, 
            bg=THEME['bg_main'], 
            highlightbackground=THEME['fg_navbar'], 
            highlightthickness=1, 
            bd=0
        )
        self.entry_frame.pack(fill="x")
        
        self.entry = tk.Entry(
            self.entry_frame, 
            fg=THEME['fg_primary'], 
            bg=THEME['bg_main'], 
            insertbackground=THEME['accent_primary'], 
            font=THEME['font_body'], 
            show=show, 
            bd=0, 
            relief="flat"
        )
        self.entry.pack(fill="x", padx=10, pady=8)

        # Highlight on focus
        self.entry.bind("<FocusIn>", lambda e: self.entry_frame.config(highlightbackground=THEME['accent_primary']))
        self.entry.bind("<FocusOut>", lambda e: self.entry_frame.config(highlightbackground=THEME['fg_navbar']))

    def get(self):
        return self.entry.get()

    def clear(self):
        self.entry.delete(0, tk.END)

    def set(self, val):
        self.clear()
        self.entry.insert(0, val)

class SecureInputField(InputField):
    """
    Custom password entry widget featuring an interactive visibility toggle.
    """
    def __init__(self, master, label_text, **kwargs):
        super().__init__(master, label_text=label_text, show="*", **kwargs)
        
        # Repack entry to make room for toggle button
        self.entry.pack_forget()
        
        self.toggle_btn = tk.Label(
            self.entry_frame, 
            text="👁", 
            fg=THEME['fg_secondary'], 
            bg=THEME['bg_main'], 
            font=THEME['font_body'], 
            cursor="hand2"
        )
        self.toggle_btn.pack(side="right", padx=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=8)
        
        self.is_visible = False
        self.toggle_btn.bind("<Button-1>", self._toggle_visibility)

    def _toggle_visibility(self, event):
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.entry.config(show="")
            self.toggle_btn.config(text="🙈", fg=THEME['accent_primary'])
        else:
            self.entry.config(show="*")
            self.toggle_btn.config(text="👁", fg=THEME['fg_secondary'])

class SectionHeader(tk.Frame):
    """
    Section header with neon-accent boundary rules.
    """
    def __init__(self, master, title, **kwargs):
        super().__init__(master, bg=THEME['bg_main'], **kwargs)
        
        self.title_lbl = tk.Label(
            self, 
            text=title, 
            fg=THEME['accent_primary'], 
            bg=THEME['bg_main'], 
            font=THEME['font_h1'], 
            anchor="w"
        )
        self.title_lbl.pack(side="left")
        
        self.accent_line = tk.Frame(self, bg=THEME['accent_secondary'], height=2)
        self.accent_line.pack(fill="x", expand=True, pady=(24, 0), padx=(15, 0))
