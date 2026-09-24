FROM node:22-bookworm-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_BREAK_SYSTEM_PACKAGES=1

RUN apt-get update && apt-get install -y --no-install-recommends \
                python3 python3-pip gcc libc6-dev g++ default-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt gunicorn

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY . .

RUN useradd --create-home --uid 10001 judgey && chown -R judgey:judgey /app
USER judgey

ENV PORT=10000
EXPOSE 10000

CMD gunicorn --bind "0.0.0.0:${PORT}" --workers 2 --threads 4 --timeout 60 app:app