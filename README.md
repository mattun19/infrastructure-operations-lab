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

## Usage

公開用inventryをコピーします。

```bash
cp ansible/inventory/hosts.example.ini ansible/inventory/hosts.ini
```

環境に合わせて `host.ini` を編集後、Playbookを実行します。

```bash
ansible-playbook -i ansible/inventory/hosts.ini ansible/web.yml
```

## Notes

実環境のIPアドレスやユーザー名を含む`hosts.ini`は、
Git管理対象から除外しています。
