# プロジェクト概要：首都圏駅発車メロディアプリ

## 目的
首都圏の駅の発車メロディを再生するWebアプリケーションを開発・公開する。

## 現状
*   **メインファイル**: `rich_departure_melody_player.html`
*   **データ生成**: `generate_rich_player_html.py` が `YouTube_Videos/train_melodies.json` のデータと `rich_player_template.html` を元に `rich_departure_melody_player.html` を生成している。
*   **動作環境**:
    *   PCブラウザ: 正常に動作し、発車メロディが再生される。
    *   モバイルブラウザ（iOS/Android）: YouTube動画の再生がブロックされ、動作しない。
*   **公開方法**: GitHub Pagesでの公開を予定。

## 現在の課題
`rich_departure_melody_player.html` がモバイル環境でYouTube動画を再生できない問題を解決する。

## 解決策の仮説
YouTube IFrame Player APIの初期化パラメータがモバイル環境の自動再生ポリシーやインライン再生の要件を満たしていない可能性がある。以下のパラメータ調整を検討する。
1.  `height` と `width` を `0` 以外の値（例: `1`）に設定し、CSSで画面外に配置することで、ブラウザにプレーヤーが「表示されている」と認識させる。
2.  `playerVars` に `playsinline: 1` を追加し、iOSでのインライン再生を有効にする。
3.  `playerVars` に `origin: window.location.origin` を追加し、セキュリティ要件を満たす。

## 今後の展望
*   路線や駅数の拡張。
*   必要に応じて、追加ライブラリやサーバー環境（MCPサーバーなど）の導入を検討。

## 作業履歴

### 2025年7月6日
*   プロジェクトの現状と課題を要件定義し、`GEMINI.md` を作成。
*   モバイルでのYouTube動画再生問題の解決策として、YouTube IFrame APIの初期化パラメータ調整を特定。
*   `rich_player_template.html` に `height: '1'`, `width: '1'`, `playsinline: 1`, `origin: window.location.origin` を追加する修正を適用。
*   `generate_rich_player_html.py` を実行し、`rich_departure_melody_player.html` を再生成。
*   PCでの動作不良が報告されたため、`rich_player_template.html` の変更を全て元に戻し、`rich_departure_melody_player.html` を再生成して元の機能する状態に復元。
*   PCでの動作が正常に戻ったことを確認。モバイルでの再生問題は引き続き未解決であり、次回再検討する。

### 2025年7月12日
*   モバイルでのYouTube動画再生問題の解決策として、`rich_player_template.html` に `playsinline: 1` パラメータのみを追加してデプロイしたが、モバイルでの再生は改善されなかった。
*   次に、`playsinline: 1` に加えて `origin: window.location.origin` パラメータも追加してデプロイしたが、PCでの再生もできなくなったため、全ての変更を元に戻した。
*   PCでの動作が正常に戻ったことを確認。モバイルでの再生問題は引き続き未解決。
