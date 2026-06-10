"""Put the repository root on sys.path so the shims in this directory can drive the
v3 `mantle` package no matter where they are launched from."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
