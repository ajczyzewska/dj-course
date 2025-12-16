#!/usr/bin/env python3
"""
Debug script to verify tools are properly loaded
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.mcp_tools import TOOLS_DEFINITIONS, TOOLS_MAP
from tools.clarification_tool import CLARIFICATION_TOOL_DEFINITION, CLARIFICATION_TOOLS_MAP

print("=" * 60)
print("🔍 DEBUG: Sprawdzanie załadowanych narzędzi")
print("=" * 60)
print()

# Combine all tools
all_tools = TOOLS_DEFINITIONS + [CLARIFICATION_TOOL_DEFINITION]
all_tools_map = {**TOOLS_MAP, **CLARIFICATION_TOOLS_MAP}

print(f"📊 Liczba narzędzi: {len(all_tools)}")
print()

print("📋 Lista narzędzi:")
for i, tool in enumerate(all_tools, 1):
    print(f"  {i}. {tool['name']}")
    print(f"     Opis: {tool['description'][:80]}...")
    print()

print("=" * 60)
print("🔧 Szczegóły narzędzia 'ask_for_clarification':")
print("=" * 60)
print()

clarification_tool = CLARIFICATION_TOOL_DEFINITION
print(f"Nazwa: {clarification_tool['name']}")
print(f"\nOpis:\n{clarification_tool['description']}")
print(f"\nParametry: {list(clarification_tool['parameters']['properties'].keys())}")
print(f"Wymagane: {clarification_tool['parameters']['required']}")
print()

print("=" * 60)
print("✅ Weryfikacja funkcji")
print("=" * 60)
print()

# Test if function is callable
if 'ask_for_clarification' in all_tools_map:
    print("✅ Funkcja 'ask_for_clarification' jest w mapie narzędzi")
    func = all_tools_map['ask_for_clarification']
    print(f"✅ Funkcja jest wywoływalna: {callable(func)}")
else:
    print("❌ Funkcja 'ask_for_clarification' NIE JEST w mapie narzędzi!")

print()
print("=" * 60)
print("🎯 Podsumowanie")
print("=" * 60)
print()
print(f"Wszystkie narzędzia: {', '.join([t['name'] for t in all_tools])}")
print()
print("Jeśli widzisz 'ask_for_clarification' powyżej, narzędzie jest poprawnie załadowane!")
print()
