# 🔐 Password Manager (OOP)

> A command-line password manager built with object-oriented Python and persistent JSON storage.
>
> Menedżer haseł działający w wierszu poleceń, zbudowany w obiektowym Pythonie z trwałym zapisem w JSON.

🇬🇧 [English](#-english) | 🇵🇱 [Polski](#-polski)

---

## 🇬🇧 English

### 🎯 Project goal

A simple but complete **password manager** that runs in the terminal. The user can add, retrieve, list and delete passwords through a menu, and **the data survives restarts** — passwords are saved to a JSON file and loaded automatically when the program starts.

The project is primarily an exercise in **object-oriented programming (OOP)**: instead of loose global variables and standalone functions, all the data and behaviour are bundled into a single `PasswordManager` class.

### 🧠 Why a class? (the OOP idea)

A class bundles **data** (what it *has*) with **methods** (what it *can do*) into one logical unit:

- **has** → a dictionary of `service: password` pairs (`self.passwords`)
- **can do** → add, retrieve, show all, delete, save, load

The alternative — a global dictionary plus separate functions — works, but the data and the functions that use it float around separately. A class ties them together, and lets you create multiple independent managers if needed.

### 🔑 Key concepts explained

#### `self` — "this particular object"

Every method takes `self` as its first parameter. `self` means *this specific manager*. When a method writes `self.passwords`, it means "the password dictionary belonging to **this** manager". You could create two managers and each would keep its own separate passwords.

```python
manager = PasswordManager()   # create an object (this runs __init__)
manager.add()                 # Python passes 'manager' as 'self' automatically
```

#### `__init__` — the constructor (auto-setup)

`__init__` runs **automatically** when an object is created. Here it does two things:

```python
def __init__(self):
    self.passwords = {}   # 1. start with an empty dictionary
    self.load()           # 2. immediately load saved passwords from disk
```

**Why this order matters:** the empty dictionary is the starting point. Then `load()` either fills it (if the file exists) or leaves it empty (if it doesn't). If the order were reversed, loaded data could get wiped by the `{}` assignment.

#### Auto-load — the object prepares itself

Because `__init__` calls `self.load()`, every new manager **loads saved passwords on creation** — no manual `load()` needed. The object is born ready to use.

#### Persistence with JSON + graceful error handling

- **`save()`** writes `self.passwords` to `passwords.json` (`json.dump`).
- **`load()`** reads it back (`json.load`), wrapped in `try/except`.

```python
def load(self):
    try:
        with open("passwords.json", "r") as file:
            self.passwords = json.load(file)
    except FileNotFoundError:
        pass  # first run: no file yet — just stay with the empty dict
```

The `try/except` handles a real situation: on the **first run** the file doesn't exist yet. Instead of crashing, the program catches `FileNotFoundError` and continues with an empty dictionary. The file is created the first time `save()` runs.

### 📋 How it works (flow)

```
start program
  → create PasswordManager()  → __init__ runs  → load() reads saved data
  → menu loop:
      1. Add      → ask service + password, store in dict
      2. Retrieve → ask service, show its password
      3. Show all → list every service:password
      4. Delete   → ask service, remove it
      5. Exit     → save() to JSON, then break
```

### 🚀 How to run

```bash
python password_manager.py
```

No external libraries needed — uses only Python's built-in `json`.

### 🛠️ Concepts practised

Object-oriented programming (`class`, `self`, `__init__`, methods) · dictionaries · JSON persistence · `try/except` error handling · menu loop

### ⚠️ Note

This is a **learning project**. Passwords are stored in plain text in the JSON file — it is **not** meant for real-world secure password storage. A production tool would encrypt the stored data.

---

## 🇵🇱 Polski

### 🎯 Cel projektu

Prosty, ale kompletny **menedżer haseł** działający w terminalu. Użytkownik może dodawać, odczytywać, wyświetlać i usuwać hasła przez menu, a **dane przetrwają restart** — hasła są zapisywane do pliku JSON i wczytywane automatycznie przy starcie programu.

Projekt to przede wszystkim ćwiczenie z **programowania obiektowego (OOP)**: zamiast luźnych zmiennych globalnych i osobnych funkcji, wszystkie dane i zachowanie są związane w jedną klasę `PasswordManager`.

### 🧠 Po co klasa? (idea OOP)

Klasa wiąże **dane** (co *ma*) z **metodami** (co *umie*) w jedną logiczną całość:

- **ma** → słownik par `serwis: hasło` (`self.passwords`)
- **umie** → dodawać, odczytywać, pokazywać wszystkie, usuwać, zapisywać, wczytywać

Alternatywa — globalny słownik plus osobne funkcje — działa, ale dane i funkcje, które ich używają, latają luzem osobno. Klasa je wiąże, a w razie potrzeby pozwala stworzyć wiele niezależnych menedżerów.

### 🔑 Kluczowe pojęcia

#### `self` — „ten konkretny obiekt"

Każda metoda przyjmuje `self` jako pierwszy parametr. `self` oznacza *tego konkretnego menedżera*. Gdy metoda pisze `self.passwords`, znaczy to „słownik haseł należący do **tego** menedżera". Można stworzyć dwa menedżery i każdy miałby własne, osobne hasła.

```python
manager = PasswordManager()   # stwórz obiekt (uruchamia się __init__)
manager.add()                 # Python sam podstawia 'manager' jako 'self'
```

#### `__init__` — konstruktor (automatyczne przygotowanie)

`__init__` uruchamia się **automatycznie** przy tworzeniu obiektu. Tutaj robi dwie rzeczy:

```python
def __init__(self):
    self.passwords = {}   # 1. zacznij od pustego słownika
    self.load()           # 2. od razu wczytaj zapisane hasła z dysku
```

**Czemu ta kolejność ma znaczenie:** pusty słownik to punkt startowy. Potem `load()` albo go wypełnia (gdy plik istnieje), albo zostawia pustym (gdy go nie ma). Przy odwrotnej kolejności wczytane dane mogłyby zostać skasowane przez przypisanie `{}`.

#### Auto-load — obiekt sam się przygotowuje

Ponieważ `__init__` woła `self.load()`, każdy nowy menedżer **wczytuje zapisane hasła przy stworzeniu** — bez ręcznego `load()`. Obiekt rodzi się gotowy do użycia.

#### Trwałość przez JSON + obsługa błędów

- **`save()`** zapisuje `self.passwords` do `passwords.json` (`json.dump`).
- **`load()`** wczytuje je z powrotem (`json.load`), owinięte w `try/except`.

```python
def load(self):
    try:
        with open("passwords.json", "r") as file:
            self.passwords = json.load(file)
    except FileNotFoundError:
        pass  # pierwsze uruchomienie: pliku jeszcze nie ma — zostań z pustym słownikiem
```

`try/except` obsługuje realną sytuację: przy **pierwszym uruchomieniu** plik jeszcze nie istnieje. Zamiast się wywalić, program łapie `FileNotFoundError` i kontynuuje z pustym słownikiem. Plik powstaje przy pierwszym wywołaniu `save()`.

### 📋 Jak to działa (przepływ)

```
start programu
  → stwórz PasswordManager()  → uruchamia się __init__  → load() wczytuje dane
  → pętla menu:
      1. Add      → zapytaj o serwis + hasło, zapisz w słowniku
      2. Retrieve → zapytaj o serwis, pokaż jego hasło
      3. Show all → wypisz wszystkie pary serwis:hasło
      4. Delete   → zapytaj o serwis, usuń go
      5. Exit     → save() do JSON, potem break
```

### 🚀 Jak uruchomić

```bash
python password_manager.py
```

Nie wymaga zewnętrznych bibliotek — używa tylko wbudowanego `json`.

### 🛠️ Ćwiczone pojęcia

Programowanie obiektowe (`class`, `self`, `__init__`, metody) · słowniki · trwałość przez JSON · obsługa błędów `try/except` · pętla menu

### ⚠️ Uwaga

To **projekt edukacyjny**. Hasła są przechowywane jako czysty tekst w pliku JSON — **nie** nadaje się do prawdziwego, bezpiecznego przechowywania haseł. Wersja produkcyjna szyfrowałaby zapisane dane.
