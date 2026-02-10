#!/usr/bin/env python
"""Create a test user for development."""

import os
import sys

# Set environment
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@127.0.0.1:5432/multiagentes'
os.environ['ENVIRONMENT'] = 'development'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("Creating test user...")

try:
    from backend.database.connection import get_db_session
    from backend.database.models import User, Organization
    from backend.services.user_service import UserService
    
    # Create session using context manager
    with get_db_session() as session:
        # Create user service
        user_service = UserService(session)
        
        # Create organization and user
        org, user = user_service.create_organization(
            name="Test Organization",
            owner_email="test@example.com",
            owner_password="Test@1234",
            owner_name="Test User"
        )
        
        session.commit()
        
        print(f"✅ Test user created successfully!")
        print(f"\nCredentials:")
        print(f"  Email: test@example.com")
        print(f"  Password: Test@1234")
        print(f"  Name: Test User")
        print(f"  Organization: {org.name}")
        print(f"  Role: {user.role.value}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
