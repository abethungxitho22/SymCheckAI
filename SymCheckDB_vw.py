"""
SymCheck AI - Simple Database Viewer
Run this to see all data in the database
"""

import sqlite3
import json
import os

# The database is in the 'instance' folder
DB_PATH = os.path.join('instance', 'symcheck.db')

def get_diagnosis_from_json(value):
    """Extract diagnosis name from JSON field"""
    if not value:
        return "N/A"
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed[0].get('name', 'Unknown')[:40]
        elif isinstance(parsed, dict):
            return parsed.get('name', 'Unknown')[:40]
        else:
            return str(value)[:40]
    except:
        return str(value)[:40]

def view_database():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found at: {DB_PATH}")
        print("   Please run the Flask app first to create the database.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 100)
    print("🩺 SYMCHECK AI - DATABASE CONTENTS")
    print("=" * 100)
    print(f"📁 Database: {DB_PATH}\n")
    
    # Show all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n{'='*100}")
        print(f"📋 TABLE: {table_name.upper()}")
        print("=" * 100)
        
        # Get data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print("(no data)")
            continue
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # For user table - simple display
        if table_name == 'user':
            print(f"{'ID':<5} {'Email':<35} {'First Name':<15} {'Last Name':<15} {'Age':<5} {'Gender':<10} {'Created':<20}")
            print("-" * 105)
            for row in rows:
                print(f"{row[0]:<5} {str(row[1])[:33]:<35} {str(row[3] or '')[:13]:<15} {str(row[4] or '')[:13]:<15} {row[5] or '':<5} {str(row[6] or '')[:8]:<10} {str(row[7])[:19]:<20}")
        
        # For medical_history table - show diagnosis properly
        elif table_name == 'medical_history':
            print(f"{'ID':<5} {'Symptoms':<45} {'Diagnosis':<35} {'Urgency':<12} {'Confidence':<10} {'Created':<20}")
            print("-" * 130)
            for row in rows:
                symptoms = (row[3][:42] + '...') if len(row[3]) > 45 else row[3]
                diagnosis = get_diagnosis_from_json(row[5])  # final_conditions column
                urgency = str(row[6] or 'N/A')[:10]
                confidence = f"{row[7] or 0:.0f}%" if row[7] else "N/A"
                created = str(row[8])[:19] if row[8] else "N/A"
                print(f"{row[0]:<5} {symptoms:<45} {diagnosis:<35} {urgency:<12} {confidence:<10} {created:<20}")
        
        # For any other tables - simple display
        else:
            print(f"Columns: {', '.join(columns)}")
            print("-" * 80)
            for i, row in enumerate(rows, 1):
                print(f"Row {i}: {dict(zip(columns, row))}")
    
    conn.close()
    print("\n" + "=" * 100)
    print("✅ Database view complete")
    print("=" * 100)

if __name__ == "__main__":
    view_database()