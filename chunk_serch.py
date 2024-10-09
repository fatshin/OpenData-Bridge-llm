import json
import os
import ollama
import MeCab
import subprocess
import sys
import traceback
import time

# mecab-configコマンドを使用して設定ファイルディレクトリを取得
def get_mecab_sysconfdir():
    try:
        sysconfdir = subprocess.getoutput("mecab-config --sysconfdir").strip()
        return sysconfdir
    except Exception as e:
        print(f"Error obtaining MeCab sysconf directory: {e}")
        return None

# 設定ファイルディレクトリを取得
sysconfdir = get_mecab_sysconfdir()

# 辞書ディレクトリも取得
dicdir = subprocess.getoutput("mecab-config --dicdir").strip()

# MeCabのTaggerを初期化
if dicdir and sysconfdir:
    try:
        tagger = MeCab.Tagger()
    except RuntimeError as e:
        print(f"MeCabの初期化に失敗しました: {e}")
        print("MeCabの設定ファイル（mecabrc）の場所を確認してください。")
        print(f"現在のMECABRC環境変数: {os.environ.get('MECABRC', 'Not set')}")
        raise

# チャンクの読み込み
chunks = []
output_dir = os.path.join(os.path.dirname(__file__), 'output_chunks')
for filename in os.listdir(output_dir):
    if filename.endswith('.json'):
        with open(os.path.join(output_dir, filename), 'r', encoding='utf-8') as file:
            chunk = json.load(file)
            chunks.append(chunk)

def extract_nouns(text):
    # MeCabで形態素解析し、名詞のみ抽出
    node = tagger.parseToNode(text)
    nouns = []
    while node:
        if node.feature.split(",")[0] == "名詞":
            nouns.append(node.surface)
        node = node.next
    return nouns

def search_chunks(query, chunks, top_k=2):
    query_nouns = set(extract_nouns(query))
    chunk_scores = {}

    for i, chunk in enumerate(chunks):
        chunk_text = json.dumps(chunk, ensure_ascii=False)
        chunk_nouns = set(extract_nouns(chunk_text))
        score = len(query_nouns.intersection(chunk_nouns))
        chunk_scores[i] = score

    # スコアでソートし、上位のチャンクを取得
    top_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for i, score in top_chunks:
        chunk = chunks[i]
        url = chunk.get('url', None)
        results.append((chunk, url))

    return results

def chat_with_ollama():
    print("チャットボットが起動しました。終了するには 'quit' と入力してください。")
    sys.stdout.flush()
    while True:
        try:
            sys.stdout.write("ユーザー: ")
            sys.stdout.flush()
            user_input = input().strip()
            if user_input.lower() == 'quit':
                break
            
            # チャンク検索
            search_results = search_chunks(user_input, chunks)
            
            # Ollamaへの問い合わせ
            prompt = f"ユーザーの質問: {user_input}\n\n検索結果:\n"
            for chunk, url in search_results:
                prompt += json.dumps(chunk, ensure_ascii=False, indent=2)
                if url:
                    prompt += f"\nURL: {url}\n"
                prompt += "\n"
            prompt += "\nこの情報を基に、ユーザーの質問に答えてください。関連するURLは、回答の最後に絶対記載してください。"
            
            print("Ollamaへの問い合わせを開始します。")
            response = ollama.chat(model='qwen2.5:1.5b', messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            print("Ollamaからの応答を受信しました。")
            
            if 'message' in response and 'content' in response['message']:
                print("チャットボット:", response['message']['content'])
            else:
                print("Ollamaからの応答がありません。")

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            traceback.print_exc()
            break

if __name__ == "__main__":
    try:
        chat_with_ollama()
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
    
    print("プログラムが終了します。30秒間スリープします。")
    time.sleep(30)