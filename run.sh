#!/bin/bash

# デフォルトのパスを設定
DEFAULT_PATH="./output_json/service_catalog.json"

# コマンドライン引数からパスを取得（指定されていない場合はデフォルトを使用）
SERVICE_CATALOG_PATH=${1:-$DEFAULT_PATH}

# 絶対パスに変換
SERVICE_CATALOG_PATH=$(realpath "$SERVICE_CATALOG_PATH")

# Dockerコンテナ内のパスに変換
DOCKER_PATH="/work/output_json/service_catalog.json"

# 環境変数をエクスポート
export HOST_SERVICE_CATALOG_PATH=$SERVICE_CATALOG_PATH
export DOCKER_SERVICE_CATALOG_PATH=$DOCKER_PATH

# docker-composeコマンドを実行
docker compose up --build
