"""
Database Management CLI
Easy commands to manage and seed the database
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seeder import seed_database, reset_database
from inspect_db import inspect_database, view_table_data


def print_menu():
    """Print CLI menu"""
    print("\n" + "="*80)
    print("🚗 AUTOMOTIVE DSS - DATABASE MANAGEMENT")
    print("="*80)
    print("\nAvailable Commands:")
    print("  1. seed       - Populate database with 100+ fake records")
    print("  2. reset      - Delete all data and reset database")
    print("  3. inspect    - View database schema and statistics")
    print("  4. view       - View data from specific table")
    print("  5. help       - Show this menu")
    print("  6. exit       - Exit the program")
    print("\nUsage:")
    print("  python manage.py seed")
    print("  python manage.py reset")
    print("  python manage.py inspect")
    print("  python manage.py view <table_name>")
    print("\n" + "="*80 + "\n")


def main():
    """Main CLI handler"""
    if len(sys.argv) < 2:
        print_menu()
        return
    
    command = sys.argv[1].lower()
    
    if command == "seed":
        seed_database()
    
    elif command == "reset":
        confirm = input("⚠️  WARNING: This will delete ALL data. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            reset_database()
        else:
            print("Reset cancelled.\n")
    
    elif command == "inspect":
        inspect_database()
    
    elif command == "view":
        if len(sys.argv) < 3:
            print("Usage: python manage.py view <table_name>")
            print("Example: python manage.py view teams")
            sys.exit(1)
        table_name = sys.argv[2].lower()
        view_table_data(table_name, limit=20)
    
    elif command == "help":
        print_menu()
    
    elif command == "exit":
        print("Goodbye! 👋\n")
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        print_menu()
        sys.exit(1)


if __name__ == "__main__":
    main()
