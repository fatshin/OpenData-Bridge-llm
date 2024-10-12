FROM python:3.12

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    gnupg \
    dirmngr \
    && apt-get clean && rm -rf /var/lib/apt/lists/*



# MeCabとその依存関係のインストール
RUN apt-get update && apt-get install -y \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    git \
    make \
    curl \
    xz-utils \
    file \
    sudo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy MeCab configuration file
RUN cp /etc/mecabrc /usr/local/etc/

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV MECABRC /usr/local/etc/mecabrc
ENV FLASK_APP chunk_serch_webui.py
ENV PORT 8080
ENV OLLAMA_MODEL qwen2.5-coder:1.5b

# Expose the port the app runs on
EXPOSE 8080

# Run Ollama, pull the model, and start the application
CMD ollama serve & \
    ollama pull ${OLLAMA_MODEL} && \
    python chunk_serch_webui.py
