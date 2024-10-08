# odbpipelineのアウトプットからLLMチャットボットで会話するツール
## 設定上の注意
docker-compose.yaml内の12行目　- /yourpath/output_json/service_catalog.json:/output_json/service_catalog.jsonのyourpathをご自身の環境のjsonファイルの場所に変更してください。
llmのモデルダウンロードからスタートするので、実行までかなり時間がかかります。
また、現在チューニング中ですが、LLMに質問して回答を得るまで5分弱かかります。
## 以下のgit clone後は以下のコマンドで実行してください
docker compose build && docker compose run --rm data-processor
