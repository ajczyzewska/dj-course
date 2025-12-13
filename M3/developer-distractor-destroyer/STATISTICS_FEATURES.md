# Nowe funkcje statystyk - Developer Distractor Destroyer

## Przegląd implementacji

Rozszerzenie zostało ulepszone o następujące funkcje:

### 1. Statystyki z podziałem na okresy czasu

#### Dostępne okresy:
- **Wszystkie dane** - wyświetla wszystkie zebrane statystyki
- **Dzień** - statystyki z bieżącego dnia
- **Tydzień** - statystyki z bieżącego tygodnia (według ISO 8601)
- **Miesiąc** - statystyki z bieżącego miesiąca
- **Zakres dat** - dowolny okres między dwiema datami

#### Implementacja:
- Dane są teraz zapisywane z timestampami w formacie:
```javascript
{
  domain: "example.com",
  seconds: 1,
  timestamp: 1734012345000,  // Unix timestamp w milisekundach
  date: "2025-12-12",        // ISO date YYYY-MM-DD
  year: 2025,
  month: 12,
  week: 50,                  // Numer tygodnia ISO
  day: 12,
  hour: 14
}
```

### 2. Filtrowanie i kumulowanie danych

#### Funkcje agregacji:
- `aggregateByDay()` - sumuje sekundy dla każdej domeny per dzień
- `aggregateByWeek()` - sumuje sekundy dla każdej domeny per tydzień
- `aggregateByMonth()` - sumuje sekundy dla każdej domeny per miesiąc
- `filterByDateRange()` - filtruje dane według zakresu dat

#### Wykorzystanie:
Użytkownik wybiera okres z rozwijanej listy i klika "Zastosuj filtr". Wykresy i listy automatycznie aktualizują się, pokazując tylko dane z wybranego okresu.

### 3. Import/Export statystyk do/z JSON

#### Export:
- Kliknij przycisk "Eksportuj JSON"
- Plik JSON zostanie automatycznie pobrany z nazwą: `developer-distractor-stats-YYYY-MM-DD.json`
- Zawiera:
  - `timeDataWithTimestamps` - szczegółowe dane z timestampami
  - `timeData` - zagregowane dane (dla kompatybilności wstecznej)
  - `gotchaStats` - statystyki blokowanych stron

#### Import:
- Kliknij przycisk "Importuj JSON"
- Wybierz plik JSON z eksportu
- Dane zostaną scalone z istniejącymi statystykami
- System waliduje format pliku przed importem

#### Format pliku JSON:
```json
{
  "version": "1.0",
  "exportDate": "2025-12-12T10:30:00.000Z",
  "data": {
    "timeDataWithTimestamps": [...],
    "timeData": {...},
    "gotchaStats": {...}
  }
}
```

## Pliki zmodyfikowane/utworzone

### Zmodyfikowane:
1. **background.js** - dodano śledzenie timestampów
2. **stats.js** - dodano funkcje filtrowania i import/export
3. **stats.html** - dodano UI dla filtrów i przycisków import/export

### Nowe:
1. **stats-utils.js** - funkcje pomocnicze do agregacji i walidacji

## Jak używać

### Filtrowanie statystyk:
1. Otwórz stronę statystyk (ikona rozszerzenia → Stats)
2. Wybierz okres z listy rozwijanej "Okres"
3. Jeśli wybrano "Zakres dat", wybierz daty początku i końca
4. Kliknij "Zastosuj filtr"

### Export statystyk:
1. Otwórz stronę statystyk
2. Kliknij "Eksportuj JSON"
3. Plik zostanie pobrany automatycznie

### Import statystyk:
1. Otwórz stronę statystyk
2. Kliknij "Importuj JSON"
3. Wybierz plik JSON z poprzedniego eksportu
4. Potwierdź import w oknie dialogowym

## Uwagi techniczne

### Kompatybilność wsteczna:
- Istniejące dane (`timeData`, `gotchaStats`) są zachowane
- Nowa struktura `timeDataWithTimestamps` jest dodawana równolegle
- Starsze instalacje będą działać, ale bez funkcji filtrowania (dopóki nie nagromadzą nowych danych)

### Wydajność:
- Dane z timestampami są zapisywane w tablicy, co może rosnąć w czasie
- Można rozważyć okresowe czyszczenie starych danych lub archiwizację

### Ograniczenia Chrome storage:
- `chrome.storage.local` ma limit ~5MB
- Przy intensywnym użyciu przez kilka miesięcy może być potrzebne czyszczenie
- Eksport pozwala na archiwizację danych przed wyczyszczeniem

## Możliwe rozszerzenia

1. Automatyczne archiwizowanie starych danych
2. Dodatkowe agregacje (np. godzinowe)
3. Wykresy liniowe pokazujące trendy w czasie
4. Porównywanie różnych okresów
5. Eksport do CSV/Excel
6. Dashboard z kluczowymi metrykami
