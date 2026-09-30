# Incident Test 01 - Nginx Service Stop

## Purpose

Nginxサービス停止時に、外部HTTP監視によって障害を検知し、
サービス復旧後に正常状態へ戻ることを確認する。

## Environment

- Target: Sakura VPS / Rocky Linux
- Web server: Nginx
- Monitoring: Python HTTP health check
- Scheduler: systemd timer
- Monitoring interval: 5 minutes

## Test Procedure

1. 正常状態でHTTP 200を確認
2. AnsibleからNginxサービスを停止
3. systemd timerによる自動監視で障害を検知
4. AnsibleからNginxサービスを起動
5. systemd timerによる自動監視で正常復帰を確認

## Result

| Time (JST) | Status | HTTP Status | Response Time | Detail |
|---|---|---:|---:|---|
| 2026-09-30 16:24:43 | UP | 200 | 110.39 ms | Normal |
| 2026-09-30 16:30:06 | DOWN | - | - | Connection refused |
| 2026-09-30 16:36:07 | UP | 200 | 125.37 ms | Recovered |

The monitoring system successfully recorded the transition:

```text
UP
↓
DOWN
↓
UP
```

Nginxの停止を外部HTTP監視で検知し、
サービス復旧後にHTTP 200へ戻ることを確認した。

## Notes

今回の試験ではNginx停止・起動の正確な実施時刻を記録していないため、
障害発生から検知までの正確な所要時間は測定していない。
今後の障害試験では操作時刻も記録し、検知時間を測定する。
