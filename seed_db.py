#!/usr/bin/env python3
"""
Database seeding script for Flask MVC Base Template.

Run this script to populate the database with initial data including
roles and test users.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.utils.seed_utils.seed_tables import main


if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        try:
            # Default to seeding all tables
            table_to_seed = sys.argv[1] if len(sys.argv) > 1 else 'all'
            
            print(f"Starting database seeding for: {table_to_seed}")
            main(table_to_seed)
            print("Database seeding completed successfully!")
            
        except Exception as e:
            print(f"Error during seeding: {str(e)}")
            sys.exit(1)