#!/usr/bin/env python
"""Run database migrations."""

import os
import sys

# Set environment
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@127.0.0.1:5432/multiagentes'
os.environ['ENVIRONMENT'] = 'development'

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from alembic.config import Config
from alembic import command

# Configure Alembic
alembic_ini_path = os.path.join(backend_path, 'alembic.ini')
alembic_cfg = Config(alembic_ini_path)
alembic_cfg.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL'])
alembic_cfg.set_main_option('script_location', os.path.join(backend_path, 'migrations'))

print("Running migrations...")
print(f"Database URL: {os.environ['DATABASE_URL']}")
print(f"Migrations path: {os.path.join(backend_path, 'migrations')}")

try:
    command.upgrade(alembic_cfg, "head")
    print("✅ Migrations completed successfully!")
except Exception as e:
    print(f"❌ Migration error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
