# ODBPipeline LLM Chatbot

このプロジェクトは、ODBPipeline（Open Data Bridge Pipeline）のアウトプットを利用して、LLM（Large Language Model）ベースのチャットボットを作成するツールです。ユーザーの質問に対して、関連するデータチャンクを検索し、Ollamaを使用して回答を生成します。

## 前提条件

- Docker
- Docker Compose

## セットアップ

1. このリポジトリをクローンします：

   ```
   git clone https://github.com/fatshin/OpenData-Bridge-llm
   cd OpenData-Bridge-llm

   ```

2. `docker-compose.yaml`ファイル内の以下の行を、あなたの環境に合わせて修正します：

   ```yaml
   - /yourpath/output_json/service_catalog.json:/output_json/service_catalog.json
   ```

   この行を、あなたの`service_catalog.json`ファイルの実際のパスに変更してください。

3. Dockerイメージをビルドし、コンテナを起動します：

   ```
   docker compose up --build
   ```

## 使用方法

1. セットアップが完了し、コンテナが起動したら、ブラウザで`http://localhost:8080`にアクセスします。

2. ウェブインターフェースが表示されるので、質問を入力し、チャットボットとの対話を開始します。

3. チャットボットは、入力された質問に基づいて関連するデータチャンクを検索し、Ollamaを使用して回答を生成します。

## 注意事項

- このプロジェクトは日本語テキストを処理するためにMeCabを使用しています。MeCabの設定ファイルが正しく配置されていることを確認してください。

- Ollamaモデル（qwen2.5-coder:1.5b）のダウンロードには時間がかかる場合があります。初回起動時は、モデルのダウンロードが完了するまでお待ちください。

- デバッグモードが有効になっているため、本番環境での使用には適していません。本番環境で使用する場合は、適切なセキュリティ対策を講じてください。

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

- Dockerとdocker-composeが正しくインストールされているか
- `service_catalog.json`ファイルのパスが正しいか
- コンテナ内でMeCabが正しく設定されているか

## 貢献

バグ報告や機能リクエストは、GitHubのIssueを通じてお願いします。プルリクエストも歓迎します。

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。
