# 🔥 Firewall Log Analyser (OOP)

> An object-oriented tool that parses firewall logs, detects suspicious IPs with machine learning, stores them in a database, and can process logs as a simulated live stream.
>
> Narzędzie obiektowe, które parsuje logi firewalla, wykrywa podejrzane IP przy użyciu uczenia maszynowego, zapisuje je do bazy danych i potrafi przetwarzać logi jako symulowany strumień na żywo.

🇬🇧 [English](#-english) | 🇵🇱 [Polski](#-polski)

---

## 🇬🇧 English

### 🎯 Project goal

A **firewall log analyser** that answers one security question: **which IP addresses are behaving suspiciously?** It parses the log, builds a behavioural profile per IP, flags outliers with an Isolation Forest model, and persists the findings. It runs in two modes: **batch** (analyse a whole file at once) and **streaming** (process the log line by line as if it were arriving live).

### 🗺️ Roadmap

- ✅ **Phase 1** — local core: parse, analyse, report, plot
- ✅ **Phase 2** — SQLite database storage + streaming simulation
- ⬜ **Phase 3** — cloud deployment (AWS S3 + Lambda + SNS alerts) (https://github.com/KristofWu/CyberSec/tree/17de7991a6da365a3c689e02feef3899277b83da/Firewall_analyser/cloud)

### 🧠 Architecture: one class, two modes

Everything lives in a single `FirewallAnalyser` class. The key design decision in Phase 2 was splitting parsing into two methods so the **same parser** works on a file *or* a buffer of streamed lines:

- `parse_to_lines(lines)` — parses any iterable of lines (the actual logic)
- `parse()` — opens the file and hands its lines to `parse_to_lines`

That one split is what makes both batch and streaming modes share the same code.

```python
# Batch mode
analyzer = FirewallAnalyser("firewall_big.log")
analyzer.run()            # parse + analyze
analyzer.report()         # print suspicious IPs
analyzer.save_to_db()     # store in SQLite
analyzer.plot()           # visualise

# Streaming mode
streamer = FirewallAnalyser("firewall_big.log")
streamer.stream()         # buffered, accumulating, writes to DB as it goes
```

### 📋 The core pipeline (Phase 1)

1. **`parse_to_lines()` / `parse()`** — firewall logs use `KEY=VALUE` format. The parser extracts `SRC`, `ACTION`, `DPT`, `PROTO` from each line into a record dict. Variables reset to `None` per line so a missing field doesn't inherit the previous line's value.

2. **`analyze()`** — groups events per IP into features (`total`, `unique_ports`, `blocked`, `blocked_ratio`) and runs an **Isolation Forest** to flag outliers (`1` = normal, `-1` = anomaly). `contamination=0.2` is the sensitivity dial.

3. **`report()` / `save_report()` / `plot()`** — console output, JSON export (with `reset_index()` so the IP survives), and a scatter plot that labels anomalies.

### 🗄️ Database storage (Phase 2)

Instead of a single overwritten JSON file, findings are stored in a **SQLite** database (`firewall.db`, table `threats`).

- **`save_to_db()`** uses a **clean-and-write** strategy: `DELETE FROM threats`, then `to_sql(...)`. This makes the operation **idempotent** — running it repeatedly always yields the same table, with no duplicates.
- Reading back uses `pandas.read_sql(...)`, which returns a DataFrame **with column names** (so the numbers are self-explanatory), unlike raw `fetchall()` tuples.

`to_sql` ↔ `read_sql` mirror each other: write a DataFrame to the DB, read it back into a DataFrame.

### 🌊 Streaming simulation (Phase 2)

Real firewalls never stop — logs arrive continuously. `stream()` simulates this and solves three classic streaming problems that show up the moment you process data in chunks:

| Problem | Symptom | Fix |
|---|---|---|
| **Chunk overwrite** | only the last chunk survived (1 attacker instead of 3) | accumulating state — one analyser for the whole stream |
| **Attacker split across chunks** | `total=20` instead of `25` | accumulate records, re-analyse the growing whole each time |
| **The tail / remainder** | last lines never processed (a missing attacker) | a final block processes the leftover buffer after the loop |

How it works:

1. Read line by line with a small delay (`time.sleep`) to mimic a live feed.
2. Collect lines into a **buffer**. Every `BUFFER_SIZE` lines, parse the chunk into the **accumulating** `self.records`, re-analyse **everything seen so far**, and save to the DB.
3. After the loop, a final `if buffer:` block processes the remaining "tail" lines that didn't fill a last full buffer.

Because state accumulates, each save writes a progressively more complete picture — so an attacker spread across several chunks is eventually seen in full, exactly as in batch mode.

![wykres](chart.png)

### 📊 Example result

On the sample log, both modes cleanly identify three attackers:

- **`203.0.113.45`** — brute-force (45 attempts, port 22 / SSH)
- **`45.155.205.211`** — port scan (15 different ports)
- **`185.220.101.33`** — hammering (port 445 / SMB)

### 🚀 How to run

```bash
pip install pandas scikit-learn matplotlib
python firewall_analyser.py
```

`firewall_big.log` must be in the same folder. The script creates `firewall.db` automatically.

### 🛠️ Tech stack & concepts

Python · pandas · scikit-learn · matplotlib · SQLite (`sqlite3`) · object-oriented programming · feature engineering · anomaly detection · **stream processing** (buffering, accumulating state, tail handling) · idempotent writes

---

## 🇵🇱 Polski

### 🎯 Cel projektu

**Analizator logów firewalla**, który odpowiada na jedno pytanie bezpieczeństwa: **które adresy IP zachowują się podejrzanie?** Parsuje log, buduje portret zachowania każdego IP, wskazuje odstających modelem Isolation Forest i utrwala wyniki. Działa w dwóch trybach: **wsadowym** (analiza całego pliku naraz) i **strumieniowym** (przetwarzanie linia po linii, jakby logi napływały na żywo).

### 🗺️ Mapa drogowa

- ✅ **Faza 1** — lokalny rdzeń: parse, analyze, report, plot
- ✅ **Faza 2** — zapis do bazy SQLite + symulacja strumienia
- ⬜ **Faza 3** — wdrożenie w chmurze (AWS S3 + Lambda + alerty SNS) (https://github.com/KristofWu/CyberSec/tree/17de7991a6da365a3c689e02feef3899277b83da/Firewall_analyser/cloud)

### 🧠 Architektura: jedna klasa, dwa tryby

Wszystko mieści się w klasie `FirewallAnalyser`. Kluczową decyzją Fazy 2 było rozdzielenie parsowania na dwie metody, żeby **ten sam parser** działał na pliku *lub* buforze linii strumienia:

- `parse_to_lines(lines)` — parsuje dowolną listę linii (właściwa logika)
- `parse()` — otwiera plik i przekazuje jego linie do `parse_to_lines`

To jedno rozdzielenie sprawia, że tryb wsadowy i strumieniowy współdzielą ten sam kod.

```python
# Tryb wsadowy
analyzer = FirewallAnalyser("firewall_big.log")
analyzer.run()            # parsuj + analizuj
analyzer.report()         # wypisz podejrzane IP
analyzer.save_to_db()     # zapisz do SQLite
analyzer.plot()           # zwizualizuj

# Tryb strumieniowy
streamer = FirewallAnalyser("firewall_big.log")
streamer.stream()         # buforuje, akumuluje, zapisuje do bazy na bieżąco
```

### 📋 Rdzeń pipeline (Faza 1)

1. **`parse_to_lines()` / `parse()`** — logi firewalla mają format `KLUCZ=WARTOŚĆ`. Parser wyłuskuje `SRC`, `ACTION`, `DPT`, `PROTO` z każdej linii do słownika. Zmienne resetują się na `None` co linię, żeby brakujące pole nie odziedziczyło wartości z poprzedniej.

2. **`analyze()`** — grupuje zdarzenia per IP w cechy (`total`, `unique_ports`, `blocked`, `blocked_ratio`) i uruchamia **Isolation Forest**, wskazując odstających (`1` = normalny, `-1` = anomalia). `contamination=0.2` to pokrętło czułości.

3. **`report()` / `save_report()` / `plot()`** — wynik na konsolę, eksport JSON (z `reset_index()`, by IP przetrwało), oraz wykres punktowy podpisujący anomalie.

### 🗄️ Zapis do bazy (Faza 2)

Zamiast jednego nadpisywanego pliku JSON, wyniki lądują w bazie **SQLite** (`firewall.db`, tabela `threats`).

- **`save_to_db()`** stosuje strategię **czyść-i-zapisz**: `DELETE FROM threats`, potem `to_sql(...)`. Czyni to operację **idempotentną** — wielokrotne uruchomienie zawsze daje tę samą tabelę, bez duplikatów.
- Odczyt przez `pandas.read_sql(...)` zwraca DataFrame **z nazwami kolumn** (więc liczby same się tłumaczą), w przeciwieństwie do gołych krotek z `fetchall()`.

`to_sql` ↔ `read_sql` są swoim lustrem: zapisz DataFrame do bazy, wczytaj z powrotem do DataFrame.

### 🌊 Symulacja strumienia (Faza 2)

Prawdziwe firewalle nigdy nie przestają — logi napływają bez końca. `stream()` to symuluje i rozwiązuje trzy klasyczne problemy strumienia, które pojawiają się, gdy tylko zaczniesz przetwarzać dane porcjami:

| Problem | Objaw | Rozwiązanie |
|---|---|---|
| **Nadpisywanie porcji** | przetrwała tylko ostatnia porcja (1 napastnik zamiast 3) | stan narastający — jeden analizator na cały strumień |
| **Napastnik pocięty na porcje** | `total=20` zamiast `25` | akumuluj rekordy, analizuj rosnącą całość za każdym razem |
| **Ogon / reszta** | ostatnie linie nieprzetworzone (brakujący napastnik) | końcowy blok przetwarza resztę bufora po pętli |

Jak działa:

1. Czyta linia po linii z małym opóźnieniem (`time.sleep`), naśladując napływ na żywo.
2. Zbiera linie do **bufora**. Co `BUFFER_SIZE` linii parsuje porcję do **narastającego** `self.records`, analizuje **wszystko, co dotąd napłynęło**, i zapisuje do bazy.
3. Po pętli końcowy blok `if buffer:` przetwarza pozostały „ogon" — linie, które nie wypełniły ostatniego pełnego bufora.

Ponieważ stan narasta, każdy zapis utrwala coraz pełniejszy obraz — więc napastnik rozłożony na kilka porcji jest w końcu widziany w całości, dokładnie jak w trybie wsadowym.

![wykres](chart.png)

### 📊 Przykładowy wynik

Na przykładowym logu oba tryby czysto wykrywają trzech napastników:

- **`203.0.113.45`** — brute-force (45 prób, port 22 / SSH)
- **`45.155.205.211`** — skanowanie portów (15 różnych portów)
- **`185.220.101.33`** — hammering (port 445 / SMB)

### 🚀 Jak uruchomić

```bash
pip install pandas scikit-learn matplotlib
python firewall_analyser.py
```

`firewall_big.log` musi być w tym samym folderze. Skrypt tworzy `firewall.db` automatycznie.

### 🛠️ Technologie i pojęcia

Python · pandas · scikit-learn · matplotlib · SQLite (`sqlite3`) · programowanie obiektowe · inżynieria cech · wykrywanie anomalii · **przetwarzanie strumieniowe** (buforowanie, stan narastający, obsługa ogona) · idempotentny zapis
