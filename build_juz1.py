#!/usr/bin/env python3
"""Build Juz 1 standalone (legacy shim — delegates to build_all.py)."""
from build_all import build_juz, write_juz
out, n, sz = write_juz(1)
print(f'Written {out.name}: {n} pages, {sz//1024} KB')
