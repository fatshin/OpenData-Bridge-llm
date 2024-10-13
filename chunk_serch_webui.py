import json
import os
import ollama
import MeCab
import subprocess
from flask import Flask, request, render_template, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
import re
import logging

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MeCabの設定ファイルディレクトリを取得
def get_mecab_sysconfdir():
    try:
        sysconfdir = subprocess.getoutput("mecab-config --sysconfdir").strip()
        return sysconfdir
    except Exception as e:
        logger.error(f"Error obtaining MeCab sysconf directory: {e}")
        return None

# 設定ファイルディレクトリを取得
sysconfdir = get_mecab_sysconfdir()

# 辞書ディレクトリも取得
dicdir = subprocess.getoutput("mecab-config --dicdir").strip()

# MeCabのTaggerを初期化
try:
    tagger = MeCab.Tagger()
except RuntimeError as e:
    logger.error(f"MeCabの初期化に失敗しました: {e}")
    logger.error(f"現在のMECABRC環境変数: {os.environ.get('MECABRC', 'Not set')}")
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
    node = tagger.parseToNode(text)
    nouns = []
    while node:
        if node.feature.split(",")[0] == "名詞":
            nouns.append(node.surface)
        node = node.next
    return nouns

def extract_keywords(text, top_n=5):
    vectorizer = TfidfVectorizer(tokenizer=extract_nouns, token_pattern=None)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    sorted_items = sorted(zip(feature_names, tfidf_matrix.toarray()[0]), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_items[:top_n]]

def expand_query(query):
    keywords = extract_keywords(query)
    expanded_query = " ".join(set(query.split() + keywords))
    return expanded_query

def extract_date(chunk):
    date_str = chunk.get('date')
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
    return datetime.min

def search_chunks(query, chunks, top_k=3):
    expanded_query = expand_query(query)
    query_nouns = set(extract_nouns(expanded_query))
    
    vectorizer = TfidfVectorizer(tokenizer=extract_nouns, token_pattern=None)
    chunk_texts = [json.dumps(chunk, ensure_ascii=False) for chunk in chunks]
    tfidf_matrix = vectorizer.fit_transform(chunk_texts + [expanded_query])
    
    cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
    
    dates = [extract_date(chunk) for chunk in chunks]
    
    current_date = datetime.now()
    max_days = (current_date - min(dates)).days if dates else 1
    date_scores = [(current_date - date).days / max_days for date in dates]
    
    final_scores = 0.7 * cosine_similarities + 0.3 * (1 - np.array(date_scores))
    
    top_indices = final_scores.argsort()[-top_k:][::-1]
    
    results = []
    for i in top_indices:
        chunk = chunks[i]
        url = chunk.get('url', None)
        date = dates[i].strftime("%Y-%m-%d") if dates[i] != datetime.min else "Unknown"
        results.append((chunk, url, cosine_similarities[i], date))
    
    return results

def is_general_conversation(text):
    general_patterns = [
        r'^こんにち[はわ]',
        r'^おはよう',
        r'^こんばん[はわ]',
        r'^よろしく',
        r'^ありがとう',
        r'^さようなら',
        r'^お元気',
        r'^調子[はわ]どう',
        r'^お久しぶり',
        r'^初めまして',
    ]
    return any(re.match(pattern, text) for pattern in general_patterns)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.form["user_input"]
        logger.info(f"Received user input: {user_input}")
        
        if is_general_conversation(user_input):
            prompt = f"""
            あなたは荒尾市の公式AIアシスタントです。以下のユーザーからの挨拶や一般的な会話に対して、
            親切で丁寧に、かつ簡潔に応答してください。荒尾市らしさを少し感じさせる回答を心がけてください。

            ユーザーの入力: {user_input}

            回答の際は、以下のガイドラインに従ってください：
            1. HTMLタグは使用せず、プレーンテキストで回答してください。
            2. 回答は2〜3文程度の簡潔なものにしてください。
            3. 荒尾市に関する具体的な情報は含めないでください。
            4. フレンドリーですが、公式アシスタントとしての品位は保ってください。絶対日本語で回答して
            """
        else:
            search_results = search_chunks(user_input, chunks)
            
            prompt = f"ユーザーの質問: {user_input}\n\n検索結果:\n"
            for chunk, url, similarity, date in search_results:
                prompt += json.dumps(chunk, ensure_ascii=False, indent=2)
                if url:
                    prompt += f"\nURL: {url}\n"
                prompt += f"類似度: {similarity:.4f}\n"
                prompt += f"日付: {date}\n\n"
            prompt += """
            ユーザーの質問に答える際は、絶対以下のフォーマットに従って回答してください：

            1. 回答は簡潔に、かつ構造化してください。
            2. 見出しには<h2></h2>タグを使用し、サブ見出しには<h3></h3>タグを使用してください。
            3. リストには<ul>と<li>タグを使用してください。
            4. 重要な情報は<strong></strong>タグで囲んで強調してください。
            5. 日付や時間は<code></code>タグで囲んでください。
            6. 回答の根拠になるURLは<a href="URL">リンクテキスト</a>の形式で記述してください。
            7. 段落の区切りには<p></p>タグを使用してください。
            8. 改行には<br>タグを使用してください。
            9. 回答の最後に、『最新の情報については、公式ウェブサイト（<a href="https://www.city.arao.lg.jp/">https://www.city.arao.lg.jp/</a>）をご確認ください。』を必ず入れてください。
            10. 情報の日付が古い場合は、その旨を明記してください。
            11. 日本語で回答してください。
            例：<h2>イベント情報</h2>

            <h3>1. 夜の万田坑イベント</h3>
            <ul>
            <li>名称：<strong>夜の万田坑で小学生対象のイベントを開催します</strong></li>
            <li>日時：<code>2019年4月18日(土) 18:30-19:30</code></li>
            <li>対象：小学1年生から6年生</li>
            <li>定員：約20名</li>
            <li>参加費：無料</li>
            </ul>

            <p>詳細は<a href="URL">万田坑夜のイベント詳細</a>をご確認ください。</p>

            <p><strong>注意：この情報は2019年のものです。最新の情報については、公式ウェブサイト（<a href="https://www.city.arao.lg.jp/">https://www.city.arao.lg.jp/</a>）をご確認ください。</strong></p>

            """
        
        response = ollama.chat(model='qwen2.5-coder:1.5b', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        
        ai_response = response['message']['content']
        
        if not is_general_conversation(user_input) and len(ai_response.split()) < 20:
            ai_response += "\n\n<p>この情報は役立ちましたか？荒尾市について、もっと詳しく知りたいことや、他に質問はありますか？</p>"
        
        logger.info(f"AI response: {ai_response}")
        return jsonify({"response": ai_response})
    
    except Exception as e:
        logger.error(f"Error in chat function: {e}")
        return jsonify({"error": "エラーが発生しました。もう一度お試しください。"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
