#!/usr/bin/env python
"""
Entry point for running the FastAPI backend application.
This script should be run from the project root directory.
"""

import sys
import os

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
