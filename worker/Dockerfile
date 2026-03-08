FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY distiller.py .

# Set environment
ENV PYTHONUNBUFFERED=1

# Run worker
CMD ["python", "distiller.py"]
