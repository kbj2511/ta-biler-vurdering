FROM python:3.10-slim

# Installer Chrome & afhængigheder
RUN apt-get update && apt-get install -y     wget gnupg unzip curl     fonts-liberation libasound2 libatk-bridge2.0-0 libnspr4 libnss3 libxss1 libappindicator3-1 libgbm1     chromium chromium-driver &&     rm -rf /var/lib/apt/lists/*

# Sæt miljøvariabler for Chrome i headless
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/bin/chromium"

# Kopier kode og installer afhængigheder
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Kør Streamlit
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
