import sys
import json
import os

def main(input_file_path):
    # JSONファイルを読み込む処理
    with open(input_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # 出力ディレクトリを作成
    output_dir = "/output_chunks"
    os.makedirs(output_dir, exist_ok=True)

    # dataがリストであることを前提に処理
    for i, entry in enumerate(data, start=1):
        output_file_path = os.path.join(output_dir, f"chunk_{i}.json")
        save_entry_as_json(entry, output_file_path)

def save_entry_as_json(entry, output_file_path):
    # 各エントリをJSONファイルとして保存
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(entry, file, ensure_ascii=False, indent=2)
    print(f"Saved: {output_file_path}")

if __name__ == "__main__":
    # デフォルトのJSONファイルパス
    default_file_path = "/output_json/service_catalog.json"
    
    # コマンドライン引数が指定されていればそれを使用
    input_file_path = sys.argv[1] if len(sys.argv) > 1 else default_file_path
    main(input_file_path)