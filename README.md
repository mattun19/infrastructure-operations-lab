# Infrastructure Operations Lab

さくらのVPS上のRocky Linuxを対象に、Ansibleによる構成管理、
PythonによるHTTP外形監視、systemd timerによる定期実行、
障害注入・復旧確認までを実装した個人検証環境です。

ネットワーク・サーバー運用で発生する障害を、
「構築する」「監視する」「意図的に壊す」「検知する」「復旧する」
ところまで一連の流れとして検証しています。

## Architecture

```text
Windows
└─ WSL2 / Ubuntu
   ├─ Ansible
   │    │
   │    │ SSH
   │    ▼
   │  Sakura VPS
   │  Rocky Linux
   │    └─ Nginx
   │
   ├─ Python healthcheck
   │    │
   │    │ HTTP
   │    ▼
   │  /health
   │
   └─ systemd timer
        └─ 5分間隔でhealthcheckを実行
             └─ JSONLログへ記録
```

## Environment

| Component | Technology |
|---|---|
| Cloud / VPS | Sakura VPS |
| OS | Rocky Linux |
| Control node | WSL2 / Ubuntu |
| Configuration management | Ansible |
| Web server | Nginx |
| Monitoring | Python |
| Scheduler | systemd timer |
| Log format | JSON Lines (JSONL) |
| Version control | Git / GitHub |

## Implemented

- SSH公開鍵認証によるAnsible接続
- AnsibleによるOS情報取得
- 基本パッケージの自動インストール
- Nginxの自動インストール・起動・自動起動設定
- Webコンテンツおよび `/health` エンドポイントの自動配置
- Ansible Playbookの冪等性確認
- PythonによるHTTP外形監視
- HTTPステータス、応答時間、UP/DOWN状態、エラー内容の記録
- systemd timerによる5分間隔の自動監視
- JSONL形式での監視履歴保存
- サービス障害、ネットワーク障害、HTTP障害の障害試験

## Ansible Idempotency

Playbookを連続して2回実行し、
初回のみ必要な変更が行われ、2回目は変更が発生しないことを確認しました。

```text
1st run
changed > 0
failed = 0

2nd run
changed = 0
failed = 0
```

これにより、同じPlaybookを繰り返し実行しても
意図しない変更が発生しないことを確認しています。

## Monitoring

`scripts/healthcheck.py` は監視対象URLへHTTPリクエストを実行し、
以下の情報をJSONL形式で記録します。

```text
timestamp
URL
service_status (UP / DOWN)
HTTP status
response time
error
```

監視対象URLやタイムアウト値は環境変数から取得し、
実環境のIPアドレスはリポジトリへ保存しない構成としています。

実行例:

```bash
export TARGET_URL="http://YOUR_VPS_IP/health"
python3 scripts/healthcheck.py
```

systemd timerから5分間隔で自動実行しています。

## Incident Tests

異なる障害モードを意図的に発生させ、
外形監視からどのように観測されるかを比較しました。

### Test 01 - Nginx Service Stop

Nginxサービスを停止し、サービス自体が利用不能になった場合を検証しました。

```text
Nginx stopped
↓
HTTP connection failed
↓
Connection refused
↓
service_status: DOWN
```

Nginx起動後、外形監視でHTTP 200への復旧を確認しました。

Detailed report:

```text
docs/incident-reports/nginx-stop-test.md
```

### Test 02 - TCP/80 Network Block

Nginxは正常稼働させたまま、
Sakura VPSのパケットフィルターで外部からのTCP/80通信を遮断しました。

```text
Nginx: active
Internal HTTP: 200 OK
External TCP/80: blocked
↓
Connection timeout
↓
service_status: DOWN
```

実測結果:

| Item | Result |
|---|---:|
| Failure detection | 181.33 sec |
| Recovery detection | 204.49 sec |
| Error | timeout |
| HTTP after recovery | 200 |
| Response time after recovery | 144.47 ms |

Detailed report:

```text
docs/incident-reports/network-block-test.md
```

### Test 03 - HTTP Health Endpoint Failure

Nginxおよびネットワークは正常なまま、
監視対象 `/health` のみを意図的に削除しました。

```text
Nginx: active
TCP/80: reachable
/: HTTP 200
/health: HTTP 404
↓
service_status: DOWN
```

実測結果:

| Item | Result |
|---|---:|
| Failure detection | 30.39 sec |
| Recovery detection | 48.77 sec |
| HTTP status during failure | 404 |
| Response time during failure | 173.65 ms |
| HTTP after recovery | 200 |
| Response time after recovery | 161.33 ms |

Detailed report:

```text
docs/incident-reports/http-error-test.md
```

## Failure Mode Comparison

3種類の障害で、外形監視から観測される結果が異なることを確認しました。

| Failure | Server state | Network | HTTP result | Observed error |
|---|---|---|---|---|
| Nginx stop | Down | Reachable | No response | Connection refused |
| TCP/80 block | Up | Blocked | No response | Timeout |
| `/health` failure | Up | Reachable | HTTP 404 | HTTP Error 404 |

単純なUP/DOWN判定だけでなく、
レスポンス内容から障害箇所を切り分けるための情報を取得できることを確認しています。

## Repository Structure

```text
infrastructure-operations-lab/
├── README.md
├── ansible/
│   ├── inventory/
│   │   └── hosts.example.ini
│   ├── playbook.yml
│   ├── setup.yml
│   └── web.yml
├── config/
│   └── healthcheck.env.example
├── docs/
│   └── incident-reports/
│       ├── nginx-stop-test.md
│       ├── network-block-test.md
│       └── http-error-test.md
├── scripts/
│   └── healthcheck.py
└── systemd/
    ├── healthcheck.service
    └── healthcheck.timer
```

## Usage

公開用inventoryをコピーします。

```bash
cp ansible/inventory/hosts.example.ini ansible/inventory/hosts.ini
```

環境に合わせて `hosts.ini` を編集し、Playbookを実行します。

```bash
ansible-playbook \
  -i ansible/inventory/hosts.ini \
  ansible/web.yml
```

監視用設定では、実環境に合わせて監視対象URLを指定します。

```text
TARGET_URL=http://YOUR_VPS_IP/health
TIMEOUT_SECONDS=5
```

## Security

実環境固有の以下の情報はGit管理対象から除外しています。

```text
VPSの実IPアドレス
実環境用Ansible inventory
監視ログ
監視用実環境設定
SSH秘密鍵
```

GitHubには再現に必要なサンプル設定のみを公開しています。

## What I Learned

この検証を通じて、Ansibleによる構成管理だけでなく、
構築後の監視・障害検知・切り分け・復旧までを含めて
インフラ運用を一連の仕組みとして扱うことを検証しました。

特に、同じ「サービスDOWN」であっても、

```text
Connection refused
Timeout
HTTP 404
```

という観測結果の違いから、
サービス、ネットワーク、HTTPレベルのどこで異常が発生しているかを
切り分けるための情報を取得できることを確認しました。
