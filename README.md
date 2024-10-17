# OpenData-Bridge-llm

このプロジェクトは、OpenData Bridge Pipeline のアウトプットを利用して、LLM（Large Language Model）ベースのチャットボットを作成するツールです。ユーザーの質問に対して、関連するデータチャンクを検索し、Ollama を使用して回答を生成します。

## 前提条件

- Docker
- Docker Compose

## セットアップ

1. このリポジトリをクローンします：

   ```
   git clone https://github.com/fatshin/OpenData-Bridge-llm.git
   cd OpenData-Bridge-llm
   ```

2. `run.sh` スクリプトに実行権限を付与します：

   ```
   chmod +x run.sh
   ```

## 使用方法

### Unix-like システム (macOS, Linux) または Windows の Git Bash

1. 以下のコマンドを使用して、サービスを起動します。`/path/to/your/service_catalog.json` を実際の `service_catalog.json` ファイルのパスに置き換えてください：

   ```
   ./run.sh /path/to/your/service_catalog.json
   ```

   パスを指定しない場合、デフォルトのパス（./output_json/service_catalog.json）が使用されます：

   ```
   ./run.sh
   ```

### Windows (コマンドプロンプトまたは PowerShell)

1. 以下のコマンドを使用して、サービスを起動します。`C:\path\to\your\service_catalog.json` を実際の `service_catalog.json` ファイルのパスに置き換えてください：

   ```
   $env:SERVICE_CATALOG_PATH="C:\path\to\your\service_catalog.json"; docker-compose up --build
   ```

   パスを指定しない場合、デフォルトのパス（./output_json/service_catalog.json）が使用されます：

   ```
   docker-compose up --build
   ```

### 共通の手順

2. サービスが起動したら、ブラウザで `http://localhost:8080` にアクセスします。
3. ウェブインターフェースが表示されるので、質問を入力し、チャットボットとの対話を開始します。
4. チャットボットは、入力された質問に基づいて関連するデータチャンクを検索し、Ollama を使用して回答を生成します。

## 注意事項

- このプロジェクトは日本語テキストを処理するために MeCab を使用しています。MeCab の設定ファイルが正しく配置されていることを確認してください。
- Ollama モデル（schroneko
/
gemma-2-2b-jpn-it）のダウンロードには時間がかかる場合があります。初回起動時は、モデルのダウンロードが完了するまでお待ちください。
- デバッグモードが有効になっているため、本番環境での使用には適していません。本番環境で使用する場合は、適切なセキュリティ対策を講じてください。

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

- Docker と docker-compose が正しくインストールされているか
- `service_catalog.json` ファイルのパスが正しく指定されているか
- コンテナ内で MeCab が正しく設定されているか

## 貢献

バグ報告や機能リクエストは、GitHub の Issue を通じてお願いします。プルリクエストも歓迎します。

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
