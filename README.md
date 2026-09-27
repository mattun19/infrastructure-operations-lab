# Infrastructure Operations Lab

さくらのVPS上のRocky Linuxを対象に、Ansibleを用いた
インフラ構築・運用自動化を検証する個人プロジェクトです。

## Envurinment

- Control node: WSL2 / Ubuntu
- Managed node: Sakura VPS / Rocky Linux
- Configuration management: Ansible
- Web server: Nginx

## Implemented

- SSH公開鍵認証
- Ansibleによる疎通確認
- OS情報の取得
- 基本パッケージの自動インストール
- Nginxの自動構築
- Webコンテンツの自動配置
- HTTP 200レスポンス確認
- Ansibleの冪等性確認
- PythonによるHTTP外形監視
- HTTPステータス・応答時間・UP/DOWN状態のJSONL記録
- systemd timerによる5分間隔の自動監視

## Usage

公開用inventryをコピーします。

```bash
cp ansible/inventory/hosts.example.ini ansible/inventory/hosts.ini
```

環境に合わせて `host.ini` を編集後、Playbookを実行します。

```bash
ansible-playbook -i ansible/inventory/hosts.ini ansible/web.yml
```

## Monitoring

`healthcheck.py` は指定URLへHTTPリクエストを実行し、以下を記録します。

- 実行日時
- HTTPステータスコード
- UP / DOWN状態
- 応答時間
- エラー内容

監視対象URLは環境変数から読み込み、実IPアドレスはリポジトリに保存しません。

```bash
export TARGET_URL="http://YOUR_VPS_IP"
python3 scripts/healthcheck.py
```

systemd timerを使用することで、5分間隔で自動実行できます。

## Notes

実環境のIPアドレスやユーザー名を含む`hosts.ini`は、
Git管理対象から除外しています。
