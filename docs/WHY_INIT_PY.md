"""
Why __init__.py Files Exist
=============================

Python needs __init__.py to mark directories as packages.
Without them, Python won't recognize folders as importable modules.

BEFORE (without __init__.py):
├── app/
│   ├── services/
│   │   └── plant_service.py
│   └── main.py

from app.services import plant_service  ❌ ModuleNotFoundError: No module named 'app.services'

AFTER (with __init__.py):
├── app/
│   ├── __init__.py  ← Empty file that marks this as a package
│   ├── services/
│   │   ├── __init__.py  ← This too!
│   │   └── plant_service.py
│   └── main.py

from app.services import plant_service  ✅ Works!

WHY EMPTY?
==========
In Python 3.3+, __init__.py can be empty. It just needs to EXIST.
The presence of the file is the important part, not its content.

WHEN TO ADD CODE TO __init__.py?
=================================
Only if you want to re-export commonly used items:

# app/__init__.py
from app.core.config import get_settings
from app.models.domain import UserInDB, PlantInDB

# Now users can do:
from app import get_settings  # Cleaner!
# Instead of:
from app.core.config import get_settings  # Longer import path

For this project, we keep them empty because each module is imported directly.
This is a valid and common pattern!
"""
