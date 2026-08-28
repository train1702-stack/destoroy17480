# kataller.co.jp スポンサーページ → Discord 定期スクショBot

`https://www.kataller.co.jp/sponsor-top/train/` のスクリーンショットを撮って
Discordチャンネルに2時間ごとに自動投稿します。

実行方法は2通り用意しました。**PCやサーバーを常時起動しておきたくない場合は「方法A：GitHub Actions」がおすすめ**です。

---

## 事前準備：Discord Webhookを作る

1. 投稿したいDiscordチャンネルの設定（歯車アイコン）を開く
2. 「連携サービス」→「ウェブフック」→「新しいウェブフック」を作成
3. 表示された **Webhook URL** をコピー（他人に共有しないこと）

---

## 方法A：GitHub Actions（推奨・PC不要）

自分のPCを起動しっぱなしにしなくても、GitHub側が2時間ごとに自動実行してくれます。無料枠内で収まる規模です。

1. このフォルダ一式をGitHubの新しいリポジトリ（Privateでも可）にアップロード
   ```
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin <あなたのリポジトリURL>
   git push -u origin main
   ```
2. リポジトリの `Settings` → `Secrets and variables` → `Actions` → `New repository secret` で
   - Name: `DISCORD_WEBHOOK_URL`
   - Secret: 先ほどコピーしたWebhook URL

   を登録
3. `Actions` タブを開くと `Screenshot to Discord` というワークフローがあるので、
   `Run workflow` ボタンで一度手動実行して動作確認
4. 以降は `.github/workflows/screenshot.yml` の設定により **2時間ごとに自動実行**されます
   （GitHub Actionsのスケジュールは実行タイミングが数分〜十数分ずれることがありますが、仕様です）

実行間隔を変えたい場合は `screenshot.yml` 内の `cron: "0 */2 * * *"` を編集してください
（例：3時間ごとなら `0 */3 * * *`）。

---

## 方法B：自分のPC/サーバーでcron実行

常時起動しているLinux/Mac環境やサーバーがある場合はこちら。

1. 依存パッケージをインストール
   ```
   pip install -r requirements.txt
   playwright install chromium
   ```
2. Webhook URLを環境変数に設定（`.bashrc` 等に追記すると永続化されます）
   ```
   export DISCORD_WEBHOOK_URL="ここにWebhook URLを貼る"
   ```
3. 試しに1回実行して動作確認
   ```
   python3 screenshot_to_discord.py
   ```
4. `crontab -e` で以下を追加（2時間ごと・偶数時に実行する例）
   ```
   0 */2 * * * cd /path/to/discord_screenshot_bot && DISCORD_WEBHOOK_URL="ここにWebhook URLを貼る" /usr/bin/python3 screenshot_to_discord.py >> cron.log 2>&1
   ```
   ※ `/path/to/discord_screenshot_bot` は実際に配置したフォルダの絶対パスに置き換えてください。

Windowsの場合は「タスクスケジューラ」で同様に2時間おきのトリガーを作成し、
`python screenshot_to_discord.py` を実行するタスクを登録してください。

---

## ファイル構成

- `screenshot_to_discord.py` … スクショ撮影＆Discord投稿の本体スクリプト
- `requirements.txt` … 必要なPythonパッケージ
- `.github/workflows/screenshot.yml` … GitHub Actions用のスケジュール設定
- `screenshots/`（自動生成） … ローカル実行時にスクショが保存されるフォルダ

## 注意点

- 対象サイトの `robots.txt` は自動アクセスを制限する設定になっていました。個人的な監視目的であっても、
  念のためサイトの利用規約を確認の上でご利用ください。
- ページの読み込みが遅い場合は `screenshot_to_discord.py` 内の `TIMEOUT_MS` を大きくしてください。
- Discordの1ファイルあたりの添付上限（通常8MB、Nitro鯖は上限が異なる）を超えるとエラーになります。
  ページが非常に長く画像サイズが大きい場合は `full_page=True` を外して表示領域のみのスクショにするか、
  画像を圧縮する処理を追加してください。
