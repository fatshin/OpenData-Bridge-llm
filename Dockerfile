# Pythonのベースイメージを指定
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /work

# 必要なシステムパッケージをインストール
RUN apt-get update && \
    apt-get install -y mecab libmecab-dev mecab-ipadic-utf8 curl build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# MeCabの設定ファイルの確認とリンク作成
RUN ln -sf /etc/mecabrc /usr/local/etc/mecabrc

# 環境変数を設定
ENV MECABRC=/usr/local/etc/mecabrc

# Ollamaのインストール
RUN curl https://ollama.ai/install.sh | sh

# 必要なPythonライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# スクリプトをコンテナにコピー
COPY chunk_sep.py .
COPY chunk_serch.py .

# コンテナ起動時のコマンドを設定
CMD ["sh", "-c", "ollama serve & sleep 10 && ollama pull qwen2.5:3b && python chunk_sep.py /output_json/service_catalog.json && python -u chunk_serch.py"]