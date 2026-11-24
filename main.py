import os
import sys

# Backend papkasini Python yo'liga qo'shish
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")

for path in [backend_dir, current_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

from main import app
