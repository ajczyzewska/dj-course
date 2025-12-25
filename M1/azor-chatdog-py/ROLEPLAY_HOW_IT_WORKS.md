# Jak działa Role-Playing w AZØRZE? 🎭

## Przegląd architektury

AZØR używa role-playingu przez **komendę `/roleplay`**, która uruchamia autonomiczną rozmowę między dwiema personami.

## Przepływ działania krok po kroku

### 1. Użytkownik uruchamia `/roleplay` w AZØRZE

```
Użytkownik → AZØR → command_handler.py → roleplay_command()
```

[command_handler.py:97-98](src/command_handler.py#L97-L98):
```python
elif command == '/roleplay':
    roleplay_command()
```

### 2. Wybór asystentów (commands/roleplay.py)

```python
# Użytkownik wybiera 2 asystentów
persona_a = get_assistant("sparring-partner")  # np. Sparring Partner
persona_b = get_assistant("angel-investor")     # np. Angel Investor
```

### 3. Utworzenie sesji

[roleplay_session.py:31-46](src/roleplay/roleplay_session.py#L31-L46):
```python
session = RolePlayingSession.create(persona_a, persona_b)
```

Tworzy:
- **Persona A** (wrapper z własną historią)
- **Persona B** (wrapper z własną historią)
- **Wspólny LLM client** (Gemini)

### 4. Start rozmowy z initialnym promptem

```python
initial_prompt = "Mam pomysł na startup AI..."
session.start_conversation(initial_prompt, max_turns=None)
```

## Kluczowy mechanizm - Przełączanie perspektywy 🔄

To jest **najważniejsza część**! Każda persona ma swoją własną historię konwersacji, ale odpowiedzi są **wymieniane między nimi**.

### Przykład krok po kroku:

```
Initial Prompt: "Mam pomysł na startup AI do generowania dokumentacji"
```

#### **TURN 1: Sparring Partner odpowiada**

1. **Dodaj prompt do historii Sparring Partnera**:
   ```python
   persona_a.add_to_history('user', "Mam pomysł na startup...")
   ```

   Historia Sparring Partnera:
   ```
   [
     { role: 'user', text: 'Mam pomysł na startup...' }
   ]
   ```

2. **Wygeneruj odpowiedź** (LLM widzi system prompt Sparring Partnera):
   ```
   Answer1: "Konkrety poproszę. Jaki problem to rozwiązuje?"
   ```

3. **Dodaj własną odpowiedź do historii**:
   ```python
   persona_a.add_to_history('model', answer1)
   ```

   Historia Sparring Partnera:
   ```
   [
     { role: 'user', text: 'Mam pomysł na startup...' },
     { role: 'model', text: 'Konkrety poproszę...' }  ← JA TO POWIEDZIAŁEM
   ]
   ```

4. **KLUCZOWE: Dodaj do historii Angel Investora** [roleplay_session.py:151-154](src/roleplay/roleplay_session.py#L151-L154):
   ```python
   # Angel Investor widzi initial prompt + odpowiedź Sparring Partnera
   other_persona.add_to_history('user', initial_prompt)
   other_persona.add_to_history('user', answer1)
   ```

   Historia Angel Investora:
   ```
   [
     { role: 'user', text: 'Mam pomysł na startup...' },
     { role: 'user', text: 'Konkrety poproszę...' }  ← KTOŚ INNY TO POWIEDZIAŁ
   ]
   ```

#### **TURN 2: Angel Investor odpowiada**

1. **Angel Investor generuje odpowiedź** na podstawie swojej historii:
   - System prompt: Angel Investor (zadaje trudne pytania)
   - Historia: widzi initial prompt + pytanie Sparring Partnera

   ```
   Answer2: "Powiedz mi, kto konkretnie ma płacić za Twoją platformę?"
   ```

2. **Dodaj odpowiedź do historii Angel Investora**:
   ```python
   persona_b.add_to_history('model', answer2)
   ```

   Historia Angel Investora:
   ```
   [
     { role: 'user', text: 'Mam pomysł na startup...' },
     { role: 'user', text: 'Konkrety poproszę...' },
     { role: 'model', text: 'Powiedz mi, kto konkretnie...' }  ← JA TO POWIEDZIAŁEM
   ]
   ```

3. **Dodaj do historii Sparring Partnera** [roleplay_session.py:156-157](src/roleplay/roleplay_session.py#L156-L157):
   ```python
   other_persona.add_to_history('user', answer2)
   ```

   Historia Sparring Partnera:
   ```
   [
     { role: 'user', text: 'Mam pomysł na startup...' },
     { role: 'model', text: 'Konkrety poproszę...' },
     { role: 'user', text: 'Powiedz mi, kto konkretnie...' }  ← KTOŚ INNY TO POWIEDZIAŁ
   ]
   ```

#### **TURN 3: Sparring Partner odpowiada ponownie**

Sparring Partner widzi:
- Initial prompt (user)
- Swoją pierwszą odpowiedź (model)
- Pytanie Angel Investora (user) ← **to jest nowe!**

I cykl się powtarza...

## Wizualizacja perspektyw

```
┌─────────────────────────────────────┐
│   SPARRING PARTNER - Perspektywa    │
├─────────────────────────────────────┤
│ [user]  Mam pomysł na startup...    │
│ [model] Konkrety poproszę...    ←JA │
│ [user]  Powiedz, kto ma płacić? ←ON │
│ [model] Firmy IT...             ←JA │
│ [user]  Jak zweryfikowałeś?     ←ON │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   ANGEL INVESTOR - Perspektywa      │
├─────────────────────────────────────┤
│ [user]  Mam pomysł na startup...    │
│ [user]  Konkrety poproszę...    ←ON │
│ [model] Powiedz, kto ma płacić? ←JA │
│ [user]  Firmy IT...             ←ON │
│ [model] Jak zweryfikowałeś?     ←JA │
└─────────────────────────────────────┘
```

## Kod - kluczowe fragmenty

### Persona.add_to_history() - budowanie historii

[persona.py:38-49](src/roleplay/persona.py#L38-L49):
```python
def add_to_history(self, role: str, text: str):
    """
    role: 'user' lub 'model'
    - 'user' = ktoś inny mówi do mnie
    - 'model' = JA mówię
    """
    from google.genai import types

    self._conversation_history.append(
        types.Content(
            role=role,
            parts=[types.Part.from_text(text=text)]
        )
    )
```

### Persona.generate_response() - generowanie odpowiedzi

[persona.py:51-74](src/roleplay/persona.py#L51-L74):
```python
def generate_response(self, llm_client: GeminiLLMClient) -> str:
    """
    Wywołuje LLM z:
    - system_instruction = system prompt tej persony
    - contents = historia tej persony
    """
    response = llm_client.client.models.generate_content(
        model=llm_client.get_model_name(),
        contents=self._conversation_history,  # ← WŁASNA HISTORIA
        config=types.GenerateContentConfig(
            system_instruction=self.system_prompt,  # ← WŁASNA ROLA
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=512
        ),
    )
    return response.text
```

### RolePlayingSession._execute_turn() - orkiestracja

[roleplay_session.py:114-157](src/roleplay/roleplay_session.py#L114-L157):
```python
def _execute_turn(self, responding_persona, other_persona, ...):
    # 1. Dodaj wiadomość do historii odpowiadającej persony
    responding_persona.add_to_history('user', message)

    # 2. Wygeneruj odpowiedź (LLM widzi perspektywę tej persony)
    response = responding_persona.generate_response(self.llm_client)

    # 3. Dodaj odpowiedź do własnej historii
    responding_persona.add_to_history('model', response)

    # 4. KLUCZOWE: Dodaj odpowiedź do historii DRUGIEJ persony jako 'user'
    other_persona.add_to_history('user', response)
    #                              ↑
    #                    Ta persona widzi to jako
    #                    wiadomość OD KOGOŚ INNEGO
```

## Dlaczego to działa?

### 1. **Każda persona ma swoją perspektywę**
   - Sparring Partner: "JA pytam o biznes"
   - Angel Investor: "JA pytam o fundamenty"

### 2. **Role są zamieniane lokalnie**
   ```
   Sparring mówi "X"
   → w historii Sparring: role='model' (to JA)
   → w historii Angel:    role='user'  (to KTOŚ INNY)
   ```

### 3. **LLM zawsze generuje z perspektywy "JA"**
   - System prompt definiuje KIM jestem
   - Historia pokazuje CO już powiedziałem (model) i CO słyszałem (user)

## Jak AZØR tego używa?

1. **Komenda `/roleplay`** → uruchamia UI do wyboru asystentów
2. **RolePlayingSession** → orkiestruje rozmowę
3. **Persona** → zarządza perspektywą każdej persony
4. **LLM (Gemini)** → generuje odpowiedzi dla każdej persony osobno

```
/roleplay
   ↓
Wybierz asystentów
   ↓
Podaj temat
   ↓
┌─────────────────────┐
│ RolePlayingSession  │
│   start_convers...  │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  Persona A   Persona B
     │           │
     └─────┬─────┘
           ▼
        Gemini LLM
```

## Podsumowanie

**Magia** polega na tym, że:
1. Każda persona ma **własną historię konwersacji**
2. Odpowiedź jednej persony jest dodawana do historii drugiej jako **'user'** (nie 'model')
3. LLM generuje z perspektywy danej persony (system prompt + jej historia)
4. Powstaje wrażenie autonomicznej rozmowy, mimo że to jeden model generuje obie strony!

To jak granie szachów ze sobą - zmieniasz stronę planszy i grasz z perspektywy drugiego gracza, ale pamiętasz całą historię gry! 🎭♟️
