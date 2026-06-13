"""
main.py - Entry point for the DisasterOS Desktop GUI Control Panel.
Run: python main.py
"""
import sys
from gui.main_window import MainWindow

def main():
    print("="*60)
    print("  DisasterOS Desktop GUI initialized successfully.")
    print("  Launches emergency command system window...")
    print("="*60)
    
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
