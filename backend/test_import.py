#!/usr/bin/env python3

print("=== Testing imports ===")

try:
    import sys
    print(f"✅ Python {sys.version}")
    print(f"✅ Working directory: {sys.path[0]}")
except Exception as e:
    print(f"❌ sys import failed: {e}")

try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__}")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    import uvicorn
    print(f"✅ Uvicorn available")
except Exception as e:
    print(f"❌ Uvicorn import failed: {e}")

try:
    import main
    print(f"✅ main.py imported")
    if hasattr(main, 'app'):
        print(f"✅ app object found")
    else:
        print(f"❌ app object not found")
except Exception as e:
    print(f"❌ main import failed: {e}")
    import traceback
    traceback.print_exc()

print("=== Import test complete ===")
