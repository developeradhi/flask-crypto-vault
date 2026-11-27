"""
GUI Sanity Tests.
Asserts that standard Tkinter controllers boot up, styles load, and layouts construct without syntax errors.
"""
import unittest
import tkinter as tk
from pathlib import Path
import os
from database.manager import DatabaseManager
from gui.app import SecureVaultApp
from gui.pages.login import LoginPage
from gui.pages.dashboard import DashboardPage

class TestGUIApp(unittest.TestCase):
    def setUp(self):
        # Create an isolated database path
        self.test_db_path = Path(__file__).resolve().parent / "temp_gui_vault.db"
        self.db = DatabaseManager(db_path=str(self.test_db_path))
        
        # Initialize GUI App context
        self.app = SecureVaultApp(db_manager=self.db)
        # Prevent physical window flashing on developer screen
        self.app.withdraw()

    def tearDown(self):
        # Shutdown Tkinter context cleanly
        self.app.destroy()
        # Remove DB
        if self.test_db_path.exists():
            os.remove(self.test_db_path)

    def test_app_initialization(self):
        """Asserts root layout geometry and title variables load."""
        self.assertEqual(self.app.title(), "Secure File Encryption & Decryption System")
        self.assertIsNone(self.app.current_user)

    def test_page_routing_sanity(self):
        """Asserts standard pages swap and build frames without exceptions."""
        # Main content router switches to LoginPage initially
        self.assertIn(LoginPage, self.app.frames)
        self.assertIsInstance(self.app.frames[LoginPage], LoginPage)
        
        # Trigger login sequence directly for view routing test
        session_dict = {'id': 1, 'username': 'admin'}
        self.app.login_user(session_dict)
        
        # Dashboard page must construct and switch successfully
        self.assertIn(DashboardPage, self.app.frames)
        self.assertIsInstance(self.app.frames[DashboardPage], DashboardPage)
        
        # Active frame tracker check
        self.assertEqual(self.app.active_frame_class, DashboardPage)

    def test_interactive_update(self):
        """Triggers a single cycle of the Tkinter event loop to check draw calls."""
        try:
            self.app.update()
        except Exception as e:
            self.fail(f"Drawing widgets triggered runtime exception: {str(e)}")

if __name__ == "__main__":
    unittest.main()
