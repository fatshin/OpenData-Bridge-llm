@echo off
setlocal enabledelayedexpansion

REM デフォルトのパスを設定
set "DEFAULT_PATH=.\output_json\service_catalog.json"

REM コマンドライン引数からパスを取得（指定されていない場合はデフォルトを使用）
if "%~1"=="" (
    set "SERVICE_CATALOG_PATH=%DEFAULT_PATH%"
) else (
    set "SERVICE_CATALOG_PATH=%~1"
)

REM 絶対パスに変換
for %%I in ("%SERVICE_CATALOG_PATH%") do set "SERVICE_CATALOG_PATH=%%~fI"

REM Dockerコンテナ内のパスを設定
set "DOCKER_PATH=/work/output_json/service_catalog.json"

REM Windowsパスをdocker-compose用に変換
set "DOCKER_SERVICE_CATALOG_PATH=%DOCKER_PATH%"
set "HOST_SERVICE_CATALOG_PATH=%SERVICE_CATALOG_PATH:\=/%"
set "HOST_SERVICE_CATALOG_PATH=/!HOST_SERVICE_CATALOG_PATH::=!"

REM 環境変数を設定してdocker-composeを実行
set "HOST_SERVICE_CATALOG_PATH=%HOST_SERVICE_CATALOG_PATH%"
set "DOCKER_SERVICE_CATALOG_PATH=%DOCKER_SERVICE_CATALOG_PATH%"

echo Using host path: %HOST_SERVICE_CATALOG_PATH%
echo Using Docker path: %DOCKER_SERVICE_CATALOG_PATH%

docker compose up --build
