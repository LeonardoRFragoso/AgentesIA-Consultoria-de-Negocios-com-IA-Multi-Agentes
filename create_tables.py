#!/usr/bin/env python
"""Create database tables directly using SQLAlchemy."""

import os
import sys

# Set environment
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@127.0.0.1:5432/multiagentes'
os.environ['ENVIRONMENT'] = 'development'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("Creating database tables...")

try:
    from backend.database.connection import get_engine
    from backend.database.models import Base
    
    engine = get_engine()
    
    print(f"Database URL: {os.environ['DATABASE_URL']}")
    print("Creating all tables...")
    
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tables created successfully!")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated tables: {', '.join(tables)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
