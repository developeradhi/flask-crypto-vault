"""
Application Configuration and Constants.
Contains settings for UI theme styling, database paths, and security constraints.
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
LOG_DIR = BASE_DIR / "logs"
ENCRYPTED_DIR = BASE_DIR / "encrypted_files"
DECRYPTED_DIR = BASE_DIR / "decrypted_files"

# Ensure crucial runtime directories exist
for directory in [DB_DIR, LOG_DIR, ENCRYPTED_DIR, DECRYPTED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Configuration
DB_PATH = DB_DIR / "secure_vault.db"

# Log Configuration
LOG_FILE_PATH = LOG_DIR / "system.log"

# Cryptographic and Security Settings
PBKDF2_ITERATIONS = 100000
SALT_SIZE_BYTES = 16
HASH_SALT_SIZE_BYTES = 16
KEY_SIZE_BYTES = 32  # 256 bits

# User Authentication Protection Settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# UI Design System: Modern Dark Theme
THEME = {
    "bg_main": "#121212",            # Dark space canvas background
    "bg_card": "#1E1E1E",            # Slightly lighter gray for card panels
    "bg_navbar": "#181818",          # Left-side navigation drawer background
    "bg_hover": "#2D2D2D",           # Hover state highlighting for listboxes and menu elements
    "fg_primary": "#E0E6ED",         # Off-white readability primary text
    "fg_secondary": "#A0AEC0",       # Muted gray detail text
    "fg_navbar": "#8A94A6",          # Unselected navigation items
    "accent_primary": "#00ADB5",     # Neon Cyan - main buttons, progressbars, headers
    "accent_secondary": "#7F00FF",   # Amethyst Violet - secondary actions, borders
    "success": "#4CAF50",            # Standard Green indicating correct state
    "danger": "#FF3366",             # Vibrant Red indicating invalid action or error
    "warning": "#FFB300",            # Amber indicating alerts
    
    # Fonts
    "font_family": "Segoe UI",
    "font_h1": ("Segoe UI", 20, "bold"),
    "font_h2": ("Segoe UI", 14, "bold"),
    "font_body": ("Segoe UI", 10),
    "font_small": ("Segoe UI", 9),
    "font_code": ("Consolas", 10)
}
