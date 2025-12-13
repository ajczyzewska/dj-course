# Implementacja Systemu Dostępności Kierowców i Pojazdów

## Przegląd

Ten dokument opisuje implementację systemu śledzenia dostępności kierowców i pojazdów w generatorze danych TMS.

## Architektura Bazy Danych

### 1. Tabele

#### `availability_reason` - Słownik powodów dostępności/niedostępności
```sql
CREATE TABLE availability_reason (
    reason_code VARCHAR(50) PRIMARY KEY,
    reason_description VARCHAR(255) NOT NULL,
    is_available BOOLEAN NOT NULL,
    applies_to VARCHAR(20) NOT NULL -- 'DRIVER', 'VEHICLE', or 'BOTH'
);
```

**Predefiniowane kody powodów dla kierowców:**
- `WORKING` - Standardowy czas pracy kierowcy (dostępny)
- `AVAILABLE` - Kierowca dostępny do pracy (dostępny)
- `REST` - Planowany odpoczynek (niedostępny)
- `HOLIDAY` - Urlop (niedostępny)
- `SICK` - Zwolnienie lekarskie (niedostępny)
- `TRAINING` - Szkolenie/Kurs (niedostępny)

**Predefiniowane kody powodów dla pojazdów:**
- `READY` - Pojazd gotowy do użytku (dostępny)
- `MAINTENANCE` - Planowany serwis/przegląd (niedostępny)
- `BREAKDOWN` - Awaria/Naprawa (niedostępny)
- `REGISTRATION` - Badanie techniczne (niedostępny)
- `WASHING` - Mycie pojazdu (niedostępny)

#### `driver_availability` - Dostępność kierowców
```sql
CREATE TABLE driver_availability (
    id INT PRIMARY KEY,
    driver_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    reason_code VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (reason_code) REFERENCES availability_reason(reason_code)
);
```

#### `vehicle_availability` - Dostępność pojazdów
```sql
CREATE TABLE vehicle_availability (
    id INT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    reason_code VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (reason_code) REFERENCES availability_reason(reason_code)
);
```

### 2. Indeksy

Dla wydajności zapytań utworzone zostały następujące indeksy:
- `idx_driver_availability_driver` - na kolumnie `driver_id`
- `idx_driver_availability_time` - na kolumnach `start_time`, `end_time`
- `idx_vehicle_availability_vehicle` - na kolumnie `vehicle_id`
- `idx_vehicle_availability_time` - na kolumnach `start_time`, `end_time`

### 3. Powiązania

```
drivers (1) ---< (N) driver_availability
vehicles (1) ---< (N) vehicle_availability
availability_reason (1) ---< (N) driver_availability
availability_reason (1) ---< (N) vehicle_availability
```

## Implementacja w Go

### Struktura Katalogów

```
generator/
├── availability/
│   ├── model.go           # Struktury danych
│   └── availability.go    # Logika generowania
├── config/
│   └── count.go          # Konfiguracja (dodano AVAILABILITY_DAYS)
└── generator.go          # Główny generator (rozszerzony)
```

### Model Danych

#### `model.go`

Definiuje:
- `AvailabilityReason` - struktura słownika powodów
- `DriverAvailability` - struktura dostępności kierowcy
- `VehicleAvailability` - struktura dostępności pojazdu
- Stałe dla kodów powodów (np. `ReasonWorking`, `ReasonReady`)

### Generowanie Danych

#### Dostępność Kierowców (`GenerateDriverAvailability`)

Logika generowania:
1. **Weekendy** - Automatycznie generowane jako okresy `REST` (całodobowo)
2. **Dni robocze** - Losowo wybierane z następujących opcji:
   - 94% - Normalna praca (`WORKING`)
     - 70% szansa na zmianę poranną (6:00-16:00)
     - 30% szansa na zmianę wieczorną (14:00-00:00)
   - 3% - Urlop (`HOLIDAY`)
   - 2% - Zwolnienie lekarskie (`SICK`)
   - 1% - Szkolenie (`TRAINING`)

Każdy kierowca otrzymuje rekordy dla każdego dnia w skonfigurowanym okresie (`AVAILABILITY_DAYS`).

#### Dostępność Pojazdów (`GenerateVehicleAvailability`)

Logika generowania:
1. **Domyślny stan** - Pojazd jest `READY` (gotowy)
2. **Serwis planowy** (`MAINTENANCE`):
   - Co 30-60 dni
   - Trwa 4-8 godzin
   - Rodzaje: wymiana oleju, przegląd opon, układ hamulcowy, itp.
3. **Awarie** (`BREAKDOWN`):
   - 0.5% szansy dziennie
   - Trwa 2-12 godzin
   - Rodzaje: usterki silnika, układu elektrycznego, transmisji, itp.
4. **Mycie** (`WASHING`):
   - 80% szansy w każdy poniedziałek o 7:00
   - Trwa 1-2 godziny

### Generowanie SQL

Oba moduły (`GenerateDriverAvailabilityInsertStatements`, `GenerateVehicleAvailabilityInsertStatements`) generują SQL INSERT statements w formacie:

```sql
INSERT INTO driver_availability (id, driver_id, start_time, end_time, reason_code, details) VALUES
(1, 1, '2025-12-13 06:00:00', '2025-12-13 16:00:00', 'WORKING', 'Morning shift'),
(2, 1, '2025-12-14 06:00:00', '2025-12-14 16:00:00', 'WORKING', 'Morning shift'),
...
```

## Konfiguracja

W pliku [`generator/config/count.go`](generator/config/count.go):

```go
const (
    VEHICLES              = 50
    DRIVERS               = 20
    TRANSPORTATION_ORDERS = 1000
    CUSTOMERS             = 500
    AVAILABILITY_DAYS     = 30  // Liczba dni do przodu dla generowania dostępności
)
```

## Integracja z Głównym Generatorem

W [`generator/generator.go`](generator/generator.go):

1. **Faza 1**: Generowanie podstawowych encji (pojazdy, kierowcy, klienci) - równolegle
2. **Faza 2-5**: Generowanie zamówień, pozycji, timeline'ów
3. **Faza 6**: Generowanie dostępności (równolegle dla kierowców i pojazdów)
4. **Faza 7**: Kompilacja wszystkich SQL statements

Dane dostępności są dopisywane na końcu pliku SQL po wszystkich innych encjach.

## Przykładowe Zapytania

### Sprawdzenie dostępnych kierowców w danym okresie
```sql
SELECT d.first_name, d.last_name, da.start_time, da.end_time, da.reason_code
FROM drivers d
JOIN driver_availability da ON d.id = da.driver_id
JOIN availability_reason ar ON da.reason_code = ar.reason_code
WHERE ar.is_available = TRUE
  AND da.start_time <= '2025-12-20 10:00:00'
  AND da.end_time >= '2025-12-20 10:00:00';
```

### Sprawdzenie pojazdów w serwisie
```sql
SELECT v.make, v.model, va.start_time, va.end_time, va.details
FROM vehicles v
JOIN vehicle_availability va ON v.id = va.vehicle_id
WHERE va.reason_code = 'MAINTENANCE'
ORDER BY va.start_time;
```

### Znalezienie wolnych kierowców w konkretnym dniu
```sql
SELECT DISTINCT d.id, d.first_name, d.last_name
FROM drivers d
WHERE NOT EXISTS (
    SELECT 1 FROM driver_availability da
    JOIN availability_reason ar ON da.reason_code = ar.reason_code
    WHERE da.driver_id = d.id
      AND ar.is_available = FALSE
      AND DATE(da.start_time) = '2025-12-13'
);
```

## Testowanie

Aby przetestować wygenerowane dane:

```bash
cd /Users/agnieszka/repos/dj/dj-course/M3/tms-data-generator
go run ./cmd/tms-data-generator
```

Sprawdź wygenerowany plik SQL w `output/tms-latest.sql`.

## Rozszerzenia

Możliwe rozszerzenia systemu:
1. **Konflikty** - Sprawdzanie nakładających się okresów dostępności
2. **Reguły biznesowe** - Walidacja czasu pracy kierowców (45h tygodniowo, 11h dziennie max)
3. **Planowanie** - Automatyczne przypisywanie kierowców i pojazdów do zleceń na podstawie dostępności
4. **Historia** - Śledzenie zmian w dostępności (kto i kiedy zmienił)
5. **Powiadomienia** - Alert gdy pojazd wymaga serwisu lub kierowca kończy limit godzin

## Wnioski

System został zaprojektowany z myślą o:
- ✅ Realistycznych danych (zgodnie z regulacjami czasu pracy)
- ✅ Wydajności (indeksy na kluczowych kolumnach)
- ✅ Rozszerzalności (łatwe dodawanie nowych kodów powodów)
- ✅ Integralności danych (klucze obce, walidacja)
- ✅ Czytelności (jasne nazewnictwo, komentarze)
