# 1. Bazowy obraz - lekki Python 3.12 (slim = mniejszy, bez zbędnych narzędzi)
FROM python:3.12-slim

# 2. Folder roboczy wewnątrz kontenera - tu wyląduje nasz projekt
WORKDIR /app

# 3. Kopiujemy NAJPIERW tylko requirements.txt (zmienia się rzadko → cache)
COPY src/requirements.txt .

# 4. Instalujemy biblioteki (ciężki krok, ale cache'owany dopóki requirements się nie zmieni)
RUN pip install --no-cache-dir -r requirements.txt

# 5. TERAZ kopiujemy kod (zmienia się często → na końcu, żeby nie psuć cache instalacji)
COPY src/ ./src/

# 6. Kopiujemy dane
COPY data/ ./data/

# 7. Co ma się uruchomić, gdy kontener startuje
CMD ["python", "src/phishing_url_detector.py"]
