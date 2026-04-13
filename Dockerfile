FROM python:3.10-slim

WORKDIR /app

# Install Chrome untuk Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file app (tanpa .env)
COPY app/ ./app/

# Expose port
EXPOSE 7860

# Jalankan Streamlit
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=7860", "--server.address=0.0.0.0"]
