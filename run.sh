#!/bin/bash

# デフォルトのパスを設定
DEFAULT_PATH="/output_json/service_catalog.json"

# コマンドライン引数からパスを取得（指定されていない場合はデフォルトを使用）
SERVICE_CATALOG_PATH=${1:-$DEFAULT_PATH}

# Windowsパスをdocker-compose用に変換
if [[ "$OSTYPE" == "msys"* ]]; then
    SERVICE_CATALOG_PATH=$(echo $SERVICE_CATALOG_PATH | sed -e 's/\\/\//g' -e 's/://')
    SERVICE_CATALOG_PATH="/${SERVICE_CATALOG_PATH}"
fi

# 環境変数をエクスポート
export SERVICE_CATALOG_PATH

# docker-composeコマンドを実行
docker compose up --build
