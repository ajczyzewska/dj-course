#!/bin/bash
# Test script for clarification tool

echo "==================================="
echo "🧪 TEST: Funkcja doprecyzowania"
echo "==================================="
echo ""
echo "Ten test wyśle niejasne pytanie do AZØRA"
echo "i pokaże wywołanie narzędzia ask_for_clarification"
echo ""
echo "Oczekiwane zachowanie:"
echo "1. Zobaczysz: 🔧 Wywołanie narzędzia: ask_for_clarification(...)"
echo "2. AZØR zapyta o doprecyzowanie"
echo "3. Odpowiesz z więcej szczegółów"
echo "4. AZØR odpowie z pełnym kontekstem"
echo ""
echo "==================================="
echo ""
echo "Uruchamiam AZØRA..."
echo "Wpisz: zrób to"
echo ""

cd /Users/agnieszka/repos/dj/dj-course/M1/azor-chatdog-py
python src/run.py
