#!/usr/bin/env python3
"""
WATCHMAN - Telegram Home Lab Management Bot

Main entry point for the application.
Run with: python main.py
"""

import sys

from src.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
