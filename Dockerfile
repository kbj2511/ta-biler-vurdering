FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    fonts-liberation libasound2 libatk-bridge2.0-0 libnspr4 libnss3 libxss1 libappindicator3-1 libgbm1 \
    chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/bin/chromium"

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
