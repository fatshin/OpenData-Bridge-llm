@echo off
setlocal enabledelayedexpansion

REM デフォルトのパスを設定
set DEFAULT_PATH=/output_json/service_catalog.json

REM コマンドライン引数からパスを取得（指定されていない場合はデフォルトを使用）
if "%~1"=="" (
    set SERVICE_CATALOG_PATH=%DEFAULT_PATH%
) else (
    set SERVICE_CATALOG_PATH=%~1
)

REM Windowsパスをdocker-compose用に変換
set SERVICE_CATALOG_PATH=!SERVICE_CATALOG_PATH:\=/!
set SERVICE_CATALOG_PATH=!SERVICE_CATALOG_PATH::=!
set SERVICE_CATALOG_PATH=/!SERVICE_CATALOG_PATH!

REM docker-composeコマンドを実行
docker-compose up --build
