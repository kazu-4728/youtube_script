# -*- coding: utf-8 -*-
import os
import csv
import json
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- 設定項目 ---
# スクリプトの実行ディレクトリを取得
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 出力ディレクトリ名
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'YouTube_Videos')
# 検索キーワードが書かれたファイル名
KEYWORDS_FILE = os.path.join(SCRIPT_DIR, 'keywords.txt')
# CSVファイル名
CSV_FILE = 'train_melodies.csv'
# JSONファイル名
JSON_FILE = 'train_melodies.json'
# 1回の実行で取得を目指す動画の最大数
MAX_VIDEOS_TO_FETCH = 100
# 1回の実行でのAPI呼び出し上限（API無料枠保護のため）
API_CALL_LIMIT = 90

# --- グローバル変数 ---
api_calls = 0

def get_existing_video_ids(filepath):
    """既存のCSVファイルから取得済みの動画IDを読み込む"""
    if not os.path.exists(filepath):
        return set()
    
    video_ids = set()
    try:
        with open(filepath, mode='r', encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            # ヘッダーをスキップ
            try:
                next(reader)
            except StopIteration:
                return set() # 空のファイルの場合
            
            for row in reader:
                if len(row) > 2: # video_idが3列目にあると仮定
                    video_ids.add(row[2])
    except Exception as e:
        print(f"[警告] 既存のCSVファイル読み込み中にエラー: {e}")
    return video_ids

def search_videos(youtube, query, existing_ids, fetched_videos):
    """YouTube APIを呼び出して動画を検索する"""
    global api_calls
    if api_calls >= API_CALL_LIMIT:
        print("\n[情報] API呼び出し回数が上限に達したため、この回の検索はスキップします。")
        return False # 上限に達したことを示す

    try:
        print(f"\n[検索中] キーワード: '{query}'", end='')
        api_calls += 1
        
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            videoEmbeddable='true',
            maxResults=50  # 1回のAPIコールで最大50件取得
        ).execute()

        new_videos_found = 0
        skipped_count = 0
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            if video_id not in existing_ids and video_id not in [v['video_id'] for v in fetched_videos]:
                video_info = {
                    'search_query': query,
                    'video_title': item['snippet']['title'],
                    'video_id': video_id,
                    'embed_url': f'https://www.youtube.com/embed/{video_id}'
                }
                fetched_videos.append(video_info)
                new_videos_found += 1
                if len(fetched_videos) >= MAX_VIDEOS_TO_FETCH:
                    break
            else:
                skipped_count += 1
        
        print(f" -> {new_videos_found}件の新動画を発見 (重複スキップ: {skipped_count}件)")
        return True # 成功

    except HttpError as e:
        print(f"\n[エラー] APIリクエスト中にエラーが発生しました: {e}")
        # クォータ超過のエラーメッセージを判定
        if 'quotaExceeded' in str(e) or 'dailyLimitExceeded' in str(e):
            print("[重要] YouTube APIの1日の無料利用枠を使い切った可能性が高いです。")
            print("         本日のこれ以上の実行は中止します。明日以降に再試行してください。")
            return False # 致命的なエラー
        return True # 他のエラーなら続行
    except Exception as e:
        print(f"\n[エラー] 不明なエラーが発生しました: {e}")
        return True # 続行

def save_data(output_dir, fetched_videos):
    """収集したデータをCSVとJSONファイルに保存・追記する"""
    if not fetched_videos:
        print("\n[情報] 新しく追加する動画はありませんでした。")
        return

    # --- CSVに追記 ---
    csv_path = os.path.join(output_dir, CSV_FILE)
    is_new_file = not os.path.exists(csv_path)
    try:
        with open(csv_path, mode='a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow(['search_query', 'video_title', 'video_id', 'embed_url'])
            for video in fetched_videos:
                writer.writerow([video['search_query'], video['video_title'], video['video_id'], video['embed_url']])
        print(f"[成功] {len(fetched_videos)}件の動画を '{csv_path}' に追記しました。")
    except Exception as e:
        print(f"[エラー] CSVファイルへの書き込みに失敗しました: {e}")

    # --- JSONを更新 ---
    json_path = os.path.join(output_dir, JSON_FILE)
    all_videos = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                all_videos = json.load(f)
        except Exception as e:
            print(f"[警告] 既存のJSONファイルの読み込みに失敗しました: {e}")
    
    all_videos.extend(fetched_videos)
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, indent=4, ensure_ascii=False)
        print(f"[成功] JSONファイル '{json_path}' を更新しました。現在の合計: {len(all_videos)}件")
    except Exception as e:
        print(f"[エラー] JSONファイルへの書き込みに失敗しました: {e}")

def main():
    """メイン処理"""
    # APIキーの確認
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("[エラー] 環境変数 'YOUTUBE_API_KEY' が設定されていません。")
        print("         実行前に 'set YOUTUBE_API_KEY=あなたのAPIキー' を実行してください。")
        return

    # 出力ディレクトリの作成
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[情報] 出力ディレクトリ '{OUTPUT_DIR}' を作成しました。")

    # キーワードの読み込み
    if not os.path.exists(KEYWORDS_FILE):
        print(f"[エラー] キーワードファイル '{KEYWORDS_FILE}' が見つかりません。")
        return
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    # 既存データの読み込み
    csv_path = os.path.join(OUTPUT_DIR, CSV_FILE)
    existing_ids = get_existing_video_ids(csv_path)
    print(f"[情報] 既存の動画を{len(existing_ids)}件読み込みました。")

    # YouTube APIクライアントのビルド
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        print(f"[エラー] YouTube APIクライアントの初期化に失敗しました: {e}")
        return

    # 動画の検索と収集
    fetched_videos = []
    start_time = time.time()

    for query in keywords:
        if len(fetched_videos) >= MAX_VIDEOS_TO_FETCH:
            break
        
        if not search_videos(youtube, query, existing_ids, fetched_videos):
            # APIクォータ超過などの致命的なエラー
            break
        
        # APIへの負荷を軽減するための短い待機
        time.sleep(0.5)

    # データの保存
    save_data(OUTPUT_DIR, fetched_videos)

    # 最終報告
    end_time = time.time()
    print(f"\n--- 処理完了 ---")
    print(f"実行時間: {end_time - start_time:.2f}秒")
    print(f"API呼び出し回数: {api_calls} / {API_CALL_LIMIT}")
    print(f"今回新たに追加された動画数: {len(fetched_videos)}")

if __name__ == '__main__':
    main()