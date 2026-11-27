"""
Secure Vault Orchestrator.
Entry-point script of the Secure File Encryption and Decryption System.
Initializes logging and starts the GUI.
"""
import os
import sys
import logging
from pathlib import Path
from config.settings import DB_PATH, LOG_FILE_PATH, ENCRYPTED_DIR, DECRYPTED_DIR, LOG_DIR
from database.manager import DatabaseManager
from gui.app import SecureVaultApp

def setup_system_logging():
    """
    Sets up the central Python logging system, redirecting logs to file and stdout.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure logging formats
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("SecureVaultOrchestrator")

def verify_folders():
    """
    Ensures that default folders required for runtime file outputs are present.
    """
    for folder in [ENCRYPTED_DIR, DECRYPTED_DIR, LOG_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

def main():
    # Setup Log systems
    logger = setup_system_logging()
    logger.info("Initializing SecureVault runtime checks...")
    
    try:
        # Pre-execution checks
        verify_folders()
        
        # Initialize SQLite database schema
        db = DatabaseManager()
        db.log_event("INFO", "Application context initialized successfully.", "MainOrchestrator")
        logger.info("SQLite Database initialized successfully.")
        
        # Boot Tkinter Application
        logger.info("Booting Tkinter User Interface event loop...")
        app = SecureVaultApp(db_manager=db)
        app.mainloop()
        
        logger.info("Application closed down cleanly.")
        
    except Exception as e:
        logger.critical(f"FATAL: Application failed to boot: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
