import json
import os

# JSONファイルのパス
json_file_path = os.path.join('YouTube_Videos', 'train_melodies.json')
# 出力するHTMLファイルのパス
output_html_path = 'departure_melody_player.html'

def generate_html_player():
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            melodies_data = json.load(f)
    except FileNotFoundError:
        print(f"エラー: {json_file_path} が見つかりません。get_youtube_videos.py を実行してデータを作成してください。")
        return
    except json.JSONDecodeError:
        print(f"エラー: {json_file_path} のJSON形式が不正です。")
        return

    # JSONデータをJavaScriptの変数として埋め込む
    melodies_json_string = json.dumps(melodies_data, ensure_ascii=False, indent=4)

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>発車メロディ再生アプリ</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        h1 {{
            color: #0056b3;
            margin-bottom: 20px;
        }}
        #player-container {{
            width: 100%;
            max-width: 800px;
            margin-bottom: 30px;
            background-color: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        #player {{
            width: 100%;
            aspect-ratio: 16 / 9; /* 16:9 aspect ratio for YouTube videos */
        }}
        #melody-list-container {{
            width: 100%;
            max-width: 800px;
            background-color: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-radius: 8px;
            padding: 20px;
        }}
        #melody-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            max-height: 600px; /* Limit height for scrollability */
            overflow-y: auto;
        }}
        .melody-item {{
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }}
        .melody-item:last-child {{
            border-bottom: none;
        }}
        .melody-item:hover {{
            background-color: #e9e9e9;
        }}
        .melody-item strong {{
            color: #007bff;
        }}
    </style>
</head>
<body>
    <h1>発車メロディ再生アプリ</h1>

    <div id="player-container">
        <div id="player"></div>
    </div>

    <div id="melody-list-container">
        <h2>メロディリスト</h2>
        <ul id="melody-list">
            <!-- Melodies will be loaded here by JavaScript -->
        </ul>
    </div>

    <script>
        let player;
        const melodiesData = {melodies_json_string};

        // YouTube IFrame Player APIを非同期でロード
        const tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
        const firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        function onYouTubeIframeAPIReady() {{
            if (melodiesData.length > 0) {{
                player = new YT.Player('player', {{
                    height: '360',
                    width: '640',
                    videoId: melodiesData[0].video_id, // 最初の動画をデフォルトで表示
                    playerVars: {{
                        'autoplay': 0,
                        'controls': 1
                    }},
                    events: {{
                        'onReady': onPlayerReady
                    }}
                }});
            }} else {{
                console.error("No melody data found.");
            }}
        }}

        function onPlayerReady(event) {{
            // Player is ready, now populate the list
            const melodyList = document.getElementById('melody-list');
            melodiesData.forEach(melody => {{
                const listItem = document.createElement('li');
                listItem.classList.add('melody-item');
                // search_queryの二重引用符を削除
                const searchQuery = melody.search_query ? melody.search_query.replace(/"/g, '') : '';
                listItem.innerHTML = `<strong>${{searchQuery}}</strong>: ${{melody.video_title}}`;
                listItem.dataset.videoId = melody.video_id;
                listItem.addEventListener('click', () => {{
                    player.loadVideoById(melody.video_id);
                }});
                melodyList.appendChild(listItem);
            }});
        }}
    </script>
</body>
</html>"""

    try:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"'{output_html_path}' が正常に生成されました。")
        print(f"このファイルをブラウザで開いてください: file:///{os.path.abspath(output_html_path)}")
    except Exception as e:
        print(f"HTMLファイルの書き込み中にエラーが発生しました: {e}")

if __name__ == '__main__':
    # スクリプトの実行ディレクトリをカレントディレクトリに設定
    # これにより、json_file_pathが正しく解決される
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    generate_html_player()
