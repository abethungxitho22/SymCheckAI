"""
Database Viewer for SymCheck AI
Simple read-only script to display database contents
"""

import sqlite3
import json

DB_PATH = 'symcheck.db'

def print_separator(char='=', length=80):
    print(char * length)

def view_users():
    """Display all users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, created_at FROM users")
    rows = cursor.fetchall()
    
    print()
    print_separator()
    print("👤 USERS")
    print_separator()
    
    if rows:
        print(f"{'ID':<5} {'Email':<30} {'Created At':<20}")
        print_separator('-')
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<30} {row[2] if row[2] else 'N/A':<20}")
    else:
        print("No users found.")
    
    conn.close()

def view_medical_history():
    """Display all medical history records"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mh.id, u.email, mh.symptoms, mh.urgency, mh.confidence, mh.created_at 
        FROM medical_history mh
        JOIN users u ON mh.user_id = u.id
        ORDER BY mh.created_at DESC
    """)
    rows = cursor.fetchall()
    
    print()
    print_separator()
    print("🩺 MEDICAL HISTORY")
    print_separator()
    
    if rows:
        print(f"{'ID':<5} {'User':<25} {'Symptoms':<35} {'Urgency':<12} {'Confidence':<10} {'Created At':<20}")
        print_separator('-')
        for row in rows:
            symptoms = (row[2][:32] + '...') if len(row[2]) > 35 else row[2]
            confidence = f"{row[4]}%" if row[4] else 'N/A'
            print(f"{row[0]:<5} {row[1]:<25} {symptoms:<35} {str(row[3]):<12} {confidence:<10} {row[5] if row[5] else 'N/A':<20}")
    else:
        print("No medical history records found.")
    
    conn.close()

def view_detailed_history():
    """View detailed conversation for all history records"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mh.id, u.email, mh.symptoms, mh.conversation, mh.final_conditions, 
               mh.urgency, mh.confidence, mh.created_at
        FROM medical_history mh
        JOIN users u ON mh.user_id = u.id
        ORDER BY mh.created_at DESC
    """)
    rows = cursor.fetchall()
    
    if not rows:
        print("\nNo history records found.")
        conn.close()
        return
    
    for row in rows:
        print()
        print_separator()
        print(f"📋 DETAILED HISTORY (ID: {row[0]})")
        print_separator()
        print(f"User: {row[1]}")
        print(f"Symptoms: {row[2]}")
        print(f"Urgency: {row[5]}")
        print(f"Confidence: {row[6]}%" if row[6] else "Confidence: N/A")
        print(f"Created: {row[7]}")
        
        if row[3]:
            print("\n--- Conversation ---")
            try:
                conversation = json.loads(row[3])
                for msg in conversation:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    print(f"{role.upper()}: {content}")
                    print()
            except:
                print(row[3][:500])
        
        if row[4]:
            print("\n--- Final Conditions ---")
            try:
                conditions = json.loads(row[4])
                for c in conditions:
                    name = c.get('name', 'Unknown')
                    conf = c.get('confidence', 0)
                    print(f"• {name} ({conf}%)")
            except:
                print(row[4])
        
        print_separator()
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    print()
    print_separator()
    print("🩺 SYMCHECK AI - DATABASE VIEWER (READ ONLY)")
    print_separator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        view_detailed_history()
    else:
        view_users()
        view_medical_history()
        print()
        print_separator()
        print("💡 TIPS:")
        print("  • View full details: python SymCheckDB.py --detailed")
        print_separator()