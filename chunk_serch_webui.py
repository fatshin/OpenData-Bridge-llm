import json
import os
import ollama
import MeCab
import subprocess
from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime

# MeCabの設定ファイルディレクトリを取得
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

def extract_keywords(text, top_n=5):
    # TF-IDFを使用してキーワードを抽出
    vectorizer = TfidfVectorizer(tokenizer=extract_nouns, token_pattern=None)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    sorted_items = sorted(zip(feature_names, tfidf_matrix.toarray()[0]), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_items[:top_n]]

def expand_query(query):
    # ユーザー入力からキーワードを抽出し、クエリを拡張
    keywords = extract_keywords(query)
    expanded_query = " ".join(set(query.split() + keywords))
    return expanded_query

def extract_date(chunk):
    # チャンクから日付情報を抽出する関数
    # この関数は、チャンクの構造に応じて適切に実装する必要があります
    # 例えば、'date'キーがある場合はそれを使用し、なければテキスト全体から日付を抽出するなど
    date_str = chunk.get('date')
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            pass
    # 日付が見つからない場合は最も古い日付を返す
    return datetime.min

def search_chunks(query, chunks, top_k=5):
    expanded_query = expand_query(query)
    query_nouns = set(extract_nouns(expanded_query))
    
    # TF-IDFベクトライザーの初期化と適用
    vectorizer = TfidfVectorizer(tokenizer=extract_nouns, token_pattern=None)
    chunk_texts = [json.dumps(chunk, ensure_ascii=False) for chunk in chunks]
    tfidf_matrix = vectorizer.fit_transform(chunk_texts + [expanded_query])
    
    # コサイン類似度の計算
    cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
    
    # 日付情報の抽出
    dates = [extract_date(chunk) for chunk in chunks]
    
    # スコアの計算（類似度と日付の両方を考慮）
    current_date = datetime.now()
    max_days = (current_date - min(dates)).days if dates else 1
    date_scores = [(current_date - date).days / max_days for date in dates]
    
    # 類似度と日付スコアを組み合わせた最終スコアの計算
    final_scores = 0.7 * cosine_similarities + 0.3 * (1 - np.array(date_scores))
    
    # スコアでソートし、上位のチャンクを取得
    top_indices = final_scores.argsort()[-top_k:][::-1]
    
    results = []
    for i in top_indices:
        chunk = chunks[i]
        url = chunk.get('url', None)
        date = dates[i].strftime("%Y-%m-%d") if dates[i] != datetime.min else "Unknown"
        results.append((chunk, url, cosine_similarities[i], date))
    
    return results

# Flaskアプリケーションの作成
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form["user_input"]
    
    # チャンク検索
    search_results = search_chunks(user_input, chunks)
    
    # Ollamaへの問い合わせ
    prompt = f"ユーザーの質問: {user_input}\n\n検索結果:\n"
    for chunk, url, similarity, date in search_results:
        prompt += json.dumps(chunk, ensure_ascii=False, indent=2)
        if url:
            prompt += f"\nURL: {url}\n"
        prompt += f"類似度: {similarity:.4f}\n"
        prompt += f"日付: {date}\n\n"
    prompt += """
ユーザーの質問に答える際は、以下のフォーマットに従って回答してください：

1. 回答は簡潔に、かつ構造化してください。
2. 見出しには<h2></h2>タグを使用し、サブ見出しには<h3></h3>タグを使用してください。
3. リストには<ul>と<li>タグを使用してください。
4. 重要な情報は<strong></strong>タグで囲んで強調してください。
5. 日付や時間は<code></code>タグで囲んでください。
6. 回答の根拠になるURLは<a href="URL">リンクテキスト</a>の形式で絶対記述してください。
7. 段落の区切りには<p></p>タグを使用してください。
8. 改行には<br>タグを使用してください。
9. 回答の最後に、追加情報が必要な場合の問い合わせ文を入れてください。
10. 情報の日付が古い場合は、その旨を明記してください。

例：

<h2>イベント情報</h2>

<h3>1. 夜の万田坑イベント</h3>

<ul>
<li>名称：<strong>夜の万田坑で小学生対象のイベントを開催します</strong></li>
<li>日時：<code>2019年4月18日(土) 18:30-19:30</code></li>
<li>対象：小学1年生から6年生</li>
<li>定員：約20名</li>
<li>参加費：無料</li>
</ul>

<p>詳細は<a href="URL">万田坑夜のイベント詳細</a>をご確認ください。</p>

<p><strong>注意：この情報は2019年のものです。最新の情報については、公式ウェブサイトをご確認ください。</strong></p>

<p>追加情報が必要な場合は、お気軽にお問い合わせください。</p>
"""
    
    response = ollama.chat(model='qwen2.5-coder:1.5b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    
    return response['message']['content']

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
