"""
Database Inspector Script
View all tables, schemas, and data in the database
"""

from sqlalchemy import inspect, text
from src.config import engine, SessionLocal
import json

def inspect_database():
    """Inspect database tables and content"""
    
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    if not table_names:
        print("❌ No tables found in the database yet.")
        print("Tables will be created when you make API requests.\n")
        return
    
    print("=" * 80)
    print("DATABASE TABLES AND SCHEMA")
    print("=" * 80)
    print()
    
    for table_name in table_names:
        print(f"\n📊 TABLE: {table_name.upper()}")
        print("-" * 80)
        
        # Get columns
        columns = inspector.get_columns(table_name)
        print(f"\nColumns ({len(columns)}):")
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  • {col['name']:<20} {col_type:<15} {nullable}")
        
        # Get primary key
        pk = inspector.get_pk_constraint(table_name)
        if pk and pk['constrained_columns']:
            print(f"\nPrimary Key: {', '.join(pk['constrained_columns'])}")
        
        # Get foreign keys
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print(f"\nForeign Keys:")
            for fk in fks:
                print(f"  • {', '.join(fk['constrained_columns'])} → {fk['referred_table']}")
        
        # Get row count
        db = SessionLocal()
        try:
            result = db.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
            row_count = result.scalar()
            print(f"\nRow Count: {row_count}")
        except Exception as e:
            print(f"Error counting rows: {e}")
        finally:
            db.close()


def view_table_data(table_name, limit=10):
    """View data from a specific table"""
    
    db = SessionLocal()
    try:
        result = db.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
        columns = [desc[0] for desc in result.cursor.description] if result.cursor.description else []
        rows = result.fetchall()
        
        if not rows:
            print(f"\n📭 Table '{table_name}' is empty")
            return
        
        print(f"\n📋 DATA FROM '{table_name}' (showing {len(rows)} rows):")
        print("-" * 80)
        
        # Print headers
        print(" | ".join(f"{col:<15}" for col in columns))
        print("-" * 80)
        
        # Print rows
        for row in rows:
            print(" | ".join(f"{str(val):<15}" for val in row))
        
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error reading table: {e}")
    finally:
        db.close()


def show_database_info():
    """Show database file info"""
    import os
    db_path = "automotive_dss.db"
    
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"\n📁 Database File Information:")
        print(f"  Location: {os.path.abspath(db_path)}")
        print(f"  Size: {size:,} bytes ({size/1024:.2f} KB)")
    else:
        print(f"\n⚠️  Database file not found at: {os.path.abspath(db_path)}")


if __name__ == "__main__":
    show_database_info()
    print("\n")
    inspect_database()
    
    # Show sample data from each table
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        view_table_data(table_name, limit=5)
