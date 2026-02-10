#!/usr/bin/env python
"""Create Leonardo user."""

import os
import sys

# Set environment
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@127.0.0.1:5432/multiagentes'
os.environ['ENVIRONMENT'] = 'development'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("Creating Leonardo user...")

try:
    from backend.database.connection import get_db_session
    from backend.services.user_service import UserService
    
    # Create session using context manager
    with get_db_session() as session:
        # Create user service
        user_service = UserService(session)
        
        # Create organization and user
        org, user = user_service.create_organization(
            name="Leonardo Fragoso",
            owner_email="leonardorfragoso@gmail.com",
            owner_password="Valentina@2308@@",
            owner_name="Leonardo Fragoso"
        )
        
        session.commit()
        
        print(f"✅ User created successfully!")
        print(f"\nCredentials:")
        print(f"  Email: leonardorfragoso@gmail.com")
        print(f"  Password: Valentina@2308@@")
        print(f"  Name: Leonardo Fragoso")
        print(f"  Organization: {org.name}")
        print(f"  Role: {user.role.value}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
