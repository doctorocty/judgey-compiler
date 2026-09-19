import os
import sys

BACKEND_DIR = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "backend"
)

sys.path.insert(
    0,
    BACKEND_DIR
)

from backend.app import app