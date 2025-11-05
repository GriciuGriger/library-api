FROM python:3.11-slim

WORKDIR /app

# Kopiuj pliki zależności
COPY requirements.txt .

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj resztę aplikacji
COPY . .

# Uruchom aplikację
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

