# Role-Playing Module - Autonomiczna rozmowa między personami

Moduł role-playing dodaje do AZØRA możliwość prowadzenia autonomicznych rozmów między dwoma asystentami (personami).

## Funkcjonalność

- Dwie persony prowadzą dialog na zadany temat
- Każda persona ma swoją własną rolę i styl komunikacji
- Rozmowa jest w pełni autonomiczna - persony odpowiadają na siebie nawzajem
- Użytkownik może w dowolnym momencie przerwać rozmowę
- Implementacja zgodna z wzorcem z lekcji M4

## Nowi asystenci

Dodano dwa nowe asystenty zoptymalizowane do role-playingu:

### Sparring Partner (`sparring-partner`)
- Niecierpliwy inwestor startupów technologicznych
- Szuka rokujących zwrotów z inwestycji
- Komunikacja straight to the point
- Koncentruje się na business case i metrykach
- Oczekuje konkretnych liczb i planów monetyzacji

### Angel Investor (`angel-investor`)
- Wnikliwy mentor badający głębię rozumienia zagadnień
- Prowadzi rozmowę pytaniami, nie podaje gotowych odpowiedzi
- Szuka solidnych fundamentów i przemyślanych decyzji
- Wskazuje luki w myśleniu rozmówcy
- Przyjazna ale wymagająca

## Użycie

### Przez komendę `/roleplay` w AZØRZE

1. Uruchom AZØRA:
   ```bash
   cd M1/azor-chatdog-py
   python src/run.py
   ```

2. Wpisz komendę:
   ```
   /roleplay
   ```

3. Wybierz pierwszą personę (np. `sparring-partner`)

4. Wybierz drugą personę (np. `angel-investor`)

5. Podaj temat/pytanie startowe dla rozmowy

6. Rozmowa rozpocznie się automatycznie

7. Po każdej turze zostaniesz zapytany czy kontynuować:
   - Enter = kontynuuj
   - `stop` = zakończ rozmowę

### Programowo

```python
from assistant import get_assistant
from roleplay import RolePlayingSession

# Pobierz asystentów
sparring = get_assistant("sparring-partner")
angel = get_assistant("angel-investor")

# Stwórz sesję
session = RolePlayingSession.create(sparring, angel)

# Rozpocznij rozmowę
initial_prompt = "Mam pomysł na startup AI..."
session.start_conversation(initial_prompt, max_turns=10)
```

### Test

Uruchom skrypt testowy:
```bash
python test_roleplay.py
```

## Architektura

### Moduł `src/roleplay/`

#### `persona.py`
- Klasa `Persona` - wrapper na `Assistant`
- Zarządza historią konwersacji dla pojedynczej persony
- Generuje odpowiedzi używając LLM

#### `roleplay_session.py`
- Klasa `RolePlayingSession` - główny orkiestrator rozmowy
- Zarządza sekwencją tur między dwiema personami
- Buduje historię zgodnie z wzorcem z `M4/role-playing-chat`
- Przełącza kontekst między personami

### Mechanika przełączania kontekstu

Zgodnie z diagramem z `M4/role-playing-chat/flow.mermaid`:

1. **Persona A** odpowiada na initial prompt
   - Historia A: `[user: initial, model: answer1]`

2. **Persona B** widzi initial prompt + odpowiedź A
   - Historia B: `[user: initial, user: answer1]`
   - Generuje `answer2`
   - Historia B: `[user: initial, user: answer1, model: answer2]`

3. **Persona A** widzi odpowiedź B jako nową wiadomość od usera
   - Historia A: `[user: initial, model: answer1, user: answer2]`
   - Generuje `answer3`

I tak dalej...

## Przykładowa rozmowa

```
INITIAL PROMPT: Mam pomysł na startup: platforma AI do automatycznego
generowania dokumentacji technicznej z kodu źródłowego.
Czy to ma sens biznesowy?

SPARRING PARTNER: Sens biznesowy? Jasne, wszystko ma sens biznesowy,
pytanie jaki. Konkrety poproszę. Jaki problem to rozwiązuje, komu,
jak bardzo boli ten problem i ile są za to gotowi zapłacić?
No i najważniejsze - liczby. Jakie koszty, jakie przychody,
jaki model monetyzacji?

ANGEL INVESTOR: Dobrze, że myślisz o konkretach. Powiedz mi,
kto konkretnie ma płacić za Twoją platformę? Jakie stanowiska w firmie?
Jak duża jest grupa docelowa? Jakie mają alternatywne rozwiązania
i dlaczego Twoje ma być lepsze?

[...]
```

## Pliki zmodyfikowane/dodane

### Nowe pliki:
- `src/roleplay/__init__.py`
- `src/roleplay/persona.py`
- `src/roleplay/roleplay_session.py`
- `src/commands/roleplay.py`
- `test_roleplay.py`
- `ROLEPLAY.md` (ten plik)

### Zmodyfikowane pliki:
- `src/assistant/assistants_registry.py` - dodano `sparring-partner` i `angel-investor`
- `src/command_handler.py` - dodano obsługę komendy `/roleplay`
- `src/cli/console.py` - zaktualizowano help z nową komendą

## Możliwe rozszerzenia

1. **Zapis sesji role-playing** - eksport rozmowy do pliku
2. **Więcej niż 2 persony** - rozmowa okrągłego stołu
3. **Sterowanie temperaturą** - bardziej/mniej kreatywne odpowiedzi
4. **Predefiniowane scenariusze** - gotowe kombinacje person + prompty
5. **Integracja z `/session`** - możliwość zapisania rozmowy jako sesja
6. **Eksport do PDF/audio** - podobnie jak dla zwykłych sesji

## Zgodność z zadaniem M4/Z5

Implementacja spełnia wszystkie wymagania z [M4/HOMEWORK.md](../../M4/HOMEWORK.md:122-138):

✅ Rozmowa ma określone 2 "persony" (wybierane przez użytkownika)
✅ Każda persona ma określoną rolę (system prompt)
✅ Inicjalny prompt pochodzi od człowieka
✅ Agent zleca modelowi odpowiedź w roli persony A
✅ Agent przełącza kontekst modelu na personę B i zleca odpowiedź
✅ Schemat zgodny z diagramem z `M4/role-playing-chat/flow.mermaid`
✅ Tryb konwersacyjny ma swój moduł (`src/roleplay/`)
✅ UI AZØRA pobiera info od użytkownika (wybór asystentów, prompt)
✅ Możliwość przerwania konwersacji (Enter bez tekstu lub 'stop')
