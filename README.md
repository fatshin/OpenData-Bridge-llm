# ODBPipeline LLM Chatbot

このプロジェクトは、ODBPipeline（Open Data Bridge Pipeline）のアウトプットを利用して、LLM（Large Language Model）ベースのチャットボットを作成するツールです。ユーザーの質問に対して、関連するデータチャンクを検索し、Ollamaを使用して回答を生成します。

## 前提条件

- Docker
- Docker Compose

## セットアップ

1. このリポジトリをクローンします：

   ```
   git clone https://github.com/your-username/odbpipeline-llm-chatbot.git
   cd odbpipeline-llm-chatbot
   ```

2. macOS または Linux の場合、`run.sh` スクリプトに実行権限を付与します：

   ```
   chmod +x run.sh
   ```

## 使用方法

### macOS / Linux

1. 以下のコマンドを使用して、サービスを起動します。`/path/to/your/service_catalog.json` を実際の `service_catalog.json` ファイルのパスに置き換えてください：

   ```
   ./run.sh /path/to/your/service_catalog.json
   ```

   パスを指定しない場合、デフォルトのパス（/output_json/service_catalog.json）が使用されます：

   ```
   ./run.sh
   ```

### Windows

1. コマンドプロンプトまたはPowerShellで、以下のコマンドを使用してサービスを起動します。`C:\path\to\your\service_catalog.json` を実際の `service_catalog.json` ファイルのパスに置き換えてください：

   ```
   run.bat C:\path\to\your\service_catalog.json
   ```

   パスを指定しない場合、デフォルトのパス（/output_json/service_catalog.json）が使用されます：

   ```
   run.bat
   ```

### 共通の手順

2. サービスが起動したら、ブラウザで `http://localhost:8080` にアクセスします。
3. ウェブインターフェースが表示されるので、質問を入力し、チャットボットとの対話を開始します。
4. チャットボットは、入力された質問に基づいて関連するデータチャンクを検索し、Ollamaを使用して回答を生成します。

## 注意事項

- このプロジェクトは日本語テキストを処理するためにMeCabを使用しています。MeCabの設定ファイルが正しく配置されていることを確認してください。
- Ollamaモデル（qwen2.5-coder:1.5b）のダウンロードには時間がかかる場合があります。初回起動時は、モデルのダウンロードが完了するまでお待ちください。
- デバッグモードが有効になっているため、本番環境での使用には適していません。本番環境で使用する場合は、適切なセキュリティ対策を講じてください。

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

- Dockerとdocker-composeが正しくインストールされているか
- `service_catalog.json` ファイルのパスが正しく指定されているか
- コンテナ内でMeCabが正しく設定されているか

## 貢献

バグ報告や機能リクエストは、GitHubのIssueを通じてお願いします。プルリクエストも歓迎します。

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。
