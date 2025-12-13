# Instrukcja testowania blokowania stron

## Jak zainstalować rozszerzenie

1. Otwórz Chrome i wejdź na `chrome://extensions/`
2. Włącz "Tryb dewelopera" (Developer mode) w prawym górnym rogu
3. Kliknij "Załaduj rozpakowane" (Load unpacked)
4. Wybierz folder: `/Users/agnieszka/repos/dj/dj-course/M3/developer-distractor-destroyer`
5. Rozszerzenie powinno się załadować i pokazać w liście

## Jak przetestować blokowanie

### 1. Sprawdź czy blokowanie jest włączone
- Kliknij ikonę rozszerzenia w pasku narzędzi Chrome
- Sprawdź czy przycisk "Blocking Active" jest zielony (włączony)
- Jeśli jest szary, kliknij go aby włączyć

### 2. Dodaj stronę do blokowania
- W oknie popup rozszerzenia wpisz domenę do zablokowania, np.:
  - `*.linkedin.com` (już dodana domyślnie)
  - `facebook.com`
  - `*.reddit.com`
  - `twitter.com`
- Kliknij "Add Website" lub naciśnij Enter

### 3. Przetestuj blokowanie
- Spróbuj wejść na zablokowaną stronę (np. `https://www.linkedin.com`)
- Powinieneś zostać przekierowany na stronę "blocked.html" z motywacyjnym cytatem
- Sprawdź statystyki - kliknij "View Stats" w popup
- W sekcji "Gotcha Counter" powinieneś zobaczyć ile razy próbowałeś wejść na zablokowaną stronę

### 4. Sprawdź logi (opcjonalnie)
- Otwórz `chrome://extensions/`
- Znajdź "Developer Distractor Destroyer"
- Kliknij "service worker" aby otworzyć DevTools
- W zakładce Console powinieneś zobaczyć logi:
  - `tabs onUpdated` - przy każdej zmianie URL
  - `Blocking check` - sprawdzanie czy strona jest zablokowana
  - `Domain check` - wynik sprawdzenia
  - `Blocking domain` - jeśli strona jest blokowana

## Jak działają wzorce blokowania

### Dokładne dopasowanie
```
facebook.com
```
Zablokuje tylko `facebook.com`, ale NIE `www.facebook.com` ani `m.facebook.com`

### Wildcard (*)
```
*.linkedin.com
```
Zablokuje:
- `linkedin.com`
- `www.linkedin.com`
- `pl.linkedin.com`
- jakikolwiek subdomain

## Rozwiązywanie problemów

### Blokowanie nie działa

1. **Sprawdź czy blokowanie jest włączone**
   - Badge na ikonie powinien pokazywać "ON" (czerwony)

2. **Przeładuj rozszerzenie**
   - Wejdź na `chrome://extensions/`
   - Znajdź rozszerzenie i kliknij ikonę odświeżania (reload)

3. **Sprawdź uprawnienia**
   - Rozszerzenie powinno mieć uprawnienia do "Czytaj i zmieniaj wszystkie dane na odwiedzanych stronach"

4. **Sprawdź format domeny**
   - Używaj tylko nazwy domeny bez `http://` lub `https://`
   - Poprawnie: `facebook.com` lub `*.facebook.com`
   - Niepoprawnie: `https://facebook.com`

5. **Sprawdź logi w konsoli**
   - Otwórz DevTools background service worker
   - Sprawdź czy są błędy

### Gotcha stats się nie aktualizuje

- Statystyki są aktualizowane tylko gdy **faktycznie** zostaniesz zablokowany
- Odśwież stronę statystyk (F5) aby zobaczyć najnowsze dane

## Kluczowe zmiany w kodzie blokowania

### background.js linie 149-206
- `chrome.tabs.onUpdated.addListener` - nasłuchuje zmian URL
- Sprawdza zarówno `changeInfo.url` jak i `tab.url`
- Poprawione dopasowanie wildcard: `domain === baseDomain || domain.endsWith('.' + baseDomain)`
- Dodano logowanie dla debugowania

### background.js linie 208-256
- `monitorIfBlocked()` - dodatkowa warstwa sprawdzania co 3 sekundy
- Używa `lastFocusedWindow: true` dla lepszej wydajności
- Sprawdza czy lista zablokowanych stron nie jest pusta przed działaniem

## Uwagi

- Blokowanie działa tylko gdy rozszerzenie jest załadowane i włączone
- Service worker może być zatrzymany przez Chrome po bezczynności - to normalne, uruchomi się ponownie gdy będzie potrzebny
- Alarm `blocker` sprawdza aktywną kartę co 3 sekundy jako backup mechanizm
