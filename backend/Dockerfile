FROM python:3.11-slim

WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Start the API (production defaults)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

