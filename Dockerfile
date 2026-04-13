FROM python:3.10-slim

WORKDIR /app

# Install dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy semua file app
COPY app/ ./app/

# Expose port
EXPOSE 7860

# Jalankan Streamlit
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=7860", "--server.address=0.0.0.0"]
