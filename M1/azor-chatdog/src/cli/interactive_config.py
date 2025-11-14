"""
Interactive configuration module for AZOR
Allows users to configure generation parameters interactively.
"""

import os
from typing import Dict, Optional, Tuple
from cli import console


def ask_yes_no(question: str, default: bool = True) -> bool:
    """
    Ask user a yes/no question.

    Args:
        question: Question to ask
        default: Default answer if user just presses Enter

    Returns:
        True for yes, False for no
    """
    default_str = "T/n" if default else "t/N"
    while True:
        answer = input(f"{question} [{default_str}]: ").strip().lower()

        if not answer:
            return default

        if answer in ['t', 'tak', 'y', 'yes']:
            return True
        elif answer in ['n', 'nie', 'no']:
            return False
        else:
            console.print_error("Proszę odpowiedzieć 't' (tak) lub 'n' (nie)")


def ask_float(question: str, default: float, min_val: float, max_val: float) -> float:
    """
    Ask user for a float value within range.

    Args:
        question: Question to ask
        default: Default value if user just presses Enter
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Float value from user or default
    """
    while True:
        answer = input(f"{question} [{default}]: ").strip()

        if not answer:
            return default

        try:
            value = float(answer)
            if min_val <= value <= max_val:
                return value
            else:
                console.print_error(f"Wartość musi być między {min_val} a {max_val}")
        except ValueError:
            console.print_error("Proszę podać poprawną liczbę")


def ask_int(question: str, default: int, min_val: int) -> int:
    """
    Ask user for an integer value.

    Args:
        question: Question to ask
        default: Default value if user just presses Enter
        min_val: Minimum allowed value

    Returns:
        Integer value from user or default
    """
    while True:
        answer = input(f"{question} [{default}]: ").strip()

        if not answer:
            return default

        try:
            value = int(answer)
            if value >= min_val:
                return value
            else:
                console.print_error(f"Wartość musi być >= {min_val}")
        except ValueError:
            console.print_error("Proszę podać poprawną liczbę całkowitą")


def ask_for_generation_params(current_temp: float = 0.7,
                              current_top_p: float = 0.9,
                              current_top_k: int = 40) -> Dict[str, float]:
    """
    Interactively ask user for generation parameters.

    Args:
        current_temp: Current temperature value
        current_top_p: Current top_p value
        current_top_k: Current top_k value

    Returns:
        Dictionary with 'temperature', 'top_p', 'top_k' keys
    """
    console.print_info("\n🎛️  Konfiguracja parametrów generowania")
    console.print_info("=" * 50)

    # Ask if user wants to configure
    if not ask_yes_no("\nCzy chcesz skonfigurować parametry generowania?", default=False):
        console.print_info("Używam domyślnych parametrów...")
        return {
            'temperature': current_temp,
            'top_p': current_top_p,
            'top_k': current_top_k
        }

    console.print_info("\n📝 Wyjaśnienie parametrów:")
    console.print_info("  • Temperature (0.0-2.0): Kontroluje losowość/kreatywność")
    console.print_info("    - 0.0-0.3: Bardzo deterministyczne, powtarzalne odpowiedzi")
    console.print_info("    - 0.5-0.7: Zrównoważone (zalecane)")
    console.print_info("    - 0.8-1.5: Bardziej kreatywne i zróżnicowane")
    console.print_info("    - 1.5-2.0: Bardzo kreatywne, czasem chaotyczne")

    console.print_info("\n  • Top P (0.0-1.0): Nucleus sampling")
    console.print_info("    - 0.9-0.95: Zalecane dla większości przypadków")
    console.print_info("    - Niższe wartości = bardziej konserwatywne odpowiedzi")

    console.print_info("\n  • Top K (0+): Liczba najlepszych tokenów do rozważenia")
    console.print_info("    - 40-50: Dobry kompromis (zalecane)")
    console.print_info("    - 0: Wyłączone (używa tylko Top P)")

    # Ask for each parameter
    console.print_info("\n" + "=" * 50)
    temperature = ask_float(
        "\n🌡️  Temperature (kreatywność)",
        default=current_temp,
        min_val=0.0,
        max_val=2.0
    )

    top_p = ask_float(
        "🎯 Top P (nucleus sampling)",
        default=current_top_p,
        min_val=0.0,
        max_val=1.0
    )

    top_k = ask_int(
        "🔢 Top K (liczba tokenów, 0=wyłączone)",
        default=current_top_k,
        min_val=0
    )

    # Summary
    console.print_info("\n✅ Wybrane parametry:")
    console.print_info(f"   Temperature: {temperature}")
    console.print_info(f"   Top P: {top_p}")
    console.print_info(f"   Top K: {top_k}")
    console.print_info("=" * 50 + "\n")

    return {
        'temperature': temperature,
        'top_p': top_p,
        'top_k': top_k
    }


def ask_for_model_choice() -> Optional[Tuple[str, str]]:
    """
    Interactively ask user which model to use.

    Returns:
        Tuple of (model_path, model_name) or None to use default from .env
    """
    # Available models configuration
    models = {
        '1': {
            'name': 'Gemma 3 1B Q4_K_M',
            'path': os.path.expanduser('~/Library/Caches/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf'),
            'size': '~600MB RAM',
            'speed': '⚡⚡⚡ Bardzo szybki',
            'quality': '⭐⭐⭐ Dobra jakość'
        },
        '2': {
            'name': 'Gemma 2 2B Q8_0',
            'path': os.path.expanduser('~/models/gemma-2-2b-it-Q8_0.gguf'),
            'size': '~2.3GB RAM',
            'speed': '⚡⚡ Szybki',
            'quality': '⭐⭐⭐⭐ Bardzo dobra jakość'
        },
        '3': {
            'name': 'Llama 3.1 8B Q4_K_M',
            'path': os.path.expanduser('~/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'),
            'size': '~5GB RAM',
            'speed': '⚡ Wolniejszy',
            'quality': '⭐⭐⭐⭐⭐ Najlepsza jakość'
        }
    }

    console.print_info("\n🤖 Wybór modelu LLM")
    console.print_info("=" * 60)

    # Check which models are available
    available_models = {}
    for key, model in models.items():
        if os.path.exists(model['path']):
            available_models[key] = model

    if not available_models:
        console.print_error("⚠️  Nie znaleziono żadnych modeli!")
        console.print_info("Używam domyślnego z .env...")
        return None

    # Display available models
    console.print_info("\nDostępne modele:\n")
    for key in sorted(available_models.keys()):
        model = available_models[key]
        console.print_info(f"  [{key}] {model['name']}")
        console.print_info(f"      • RAM: {model['size']}")
        console.print_info(f"      • Szybkość: {model['speed']}")
        console.print_info(f"      • Jakość: {model['quality']}")
        console.print_info("")

    console.print_info("  [0] Użyj domyślnego z .env")
    console.print_info("=" * 60)

    # Ask for choice
    while True:
        choice = input("\nWybierz model [0-3]: ").strip()

        if choice == '0':
            console.print_info("Używam domyślnego modelu z .env...")
            return None

        if choice in available_models:
            selected = available_models[choice]
            console.print_info(f"\n✅ Wybrano: {selected['name']}")
            return (selected['path'], selected['name'])
        else:
            if choice in models and not os.path.exists(models[choice]['path']):
                console.print_error(f"❌ Model nie istnieje: {models[choice]['path']}")
                console.print_error("   Pobierz go najpierw lub wybierz inny model.")
            else:
                console.print_error("Nieprawidłowy wybór. Wybierz 0-3.")
