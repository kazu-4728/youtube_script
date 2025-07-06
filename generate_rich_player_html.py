import json
import os
import re

# JSONファイルのパス
json_file_path = os.path.join('YouTube_Videos', 'train_melodies.json')
# HTMLテンプレートファイルのパス
template_html_path = 'rich_player_template.html'
# 出力するHTMLファイルのパス
output_html_path = 'rich_departure_melody_player.html'

def generate_rich_html_player():
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            melodies_data = json.load(f)
    except FileNotFoundError:
        print(f"エラー: {json_file_path} が見つかりません。get_youtube_videos.py を実行してデータを作成してください。")
        return
    except json.JSONDecodeError:
        print(f"エラー: {json_file_path} のJSON形式が不正です。")
        return

    # データをstationData形式に変換
    station_data = {}
    # 路線ごとに色を割り当てるためのシンプルなハッシュ関数
    def get_color_from_string(s):
        colors = ["#9acd32", "#ff6600", "#0066cc", "#009639", "#ff0000", "#800080", "#008080", "#ffa500"]
        return colors[sum(ord(c) for c in s) % len(colors)]

    for item in melodies_data:
        # search_queryから路線名を抽出
        search_query_clean = item['search_query'].replace('"', '').strip()
        # 「発車メロディ」という文字列があれば削除
        route_name = re.sub(r'\s*発車メロディ\s*$', '', search_query_clean)
        
        # video_titleを駅名として使用（必要に応じて調整）
        station_name = item['video_title']
        video_id = item['video_id']

        if route_name not in station_data:
            station_data[route_name] = {
                "color": get_color_from_string(route_name),
                "stations": {}
            }
        
        # 同じ駅名で複数のメロディがある場合を考慮し、リストとして格納
        if station_name not in station_data[route_name]["stations"]:
            station_data[route_name]["stations"][station_name] = []
        
        station_data[route_name]["stations"][station_name].append({
            "videoId": video_id,
            "name": station_name, # ここではvideo_titleをそのまま使用
            "title": item['video_title'] # 元のvideo_titleも保持
        })

    # stationDataをJavaScriptの変数として埋め込むためのJSON文字列
    station_data_json_string = json.dumps(station_data, ensure_ascii=False, indent=4)

    try:
        with open(template_html_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"エラー: {template_html_path} が見つかりません。先に rich_player_template.html を作成してください。")
        return

    # プレースホルダーを実際のデータで置き換える
    final_html_content = template_content.replace('PLACEHOLDER_STATION_DATA', station_data_json_string)

    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(final_html_content)
        print(f"'{output_html_path}' が正常に生成されました。")
        print(f"このファイルをブラウザで開いてください: file:///{os.path.abspath(output_html_path)}")
    except Exception as e:
        print(f"HTMLファイルの書き込み中にエラーが発生しました: {e}")

if __name__ == '__main__':
    # スクリプトの実行ディレクトリをカレントディレクトリに設定
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    generate_rich_html_player()
