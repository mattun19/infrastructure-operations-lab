# Incident Test 02 - HTTP Network Block

## Purpose

Webサーバー自体は正常稼働している状態で外部からのTCP/80通信を遮断し、
HTTP外形監視がネットワーク障害を検知できることを確認する。

## Environment

- Target: Sakura VPS / Rocky Linux
- Web server: Nginx
- Monitoring: Python HTTP health check
- Scheduler: systemd timer
- Monitoring interval: 5 minutes
- Network filtering: Sakura VPS packet filter

## Test Procedure

1. Nginxがactiveであることを確認
2. VPS内部からHTTP 200が返ることを確認
3. Sakura VPSのパケットフィルターでWeb通信（TCP/80）を遮断
4. systemd timerによる外部HTTP監視でDOWNを検知
5. パケットフィルター設定を復旧
6. systemd timerによる外部HTTP監視でHTTP 200への正常復帰を確認

## Result

| Event | Time (UTC) | Result |
|---|---|---|
| Network block started | 2026-09-30 09:58:47 | TCP/80 blocked |
| Failure detected | 2026-09-30 10:01:48 | DOWN / timeout |
| Network restored | 2026-09-30 10:04:23 | TCP/80 restored |
| Recovery detected | 2026-09-30 10:07:48 | UP / HTTP 200 |

### Detection time

Network block to failure detection:

```text
181.33 seconds
= 3 minutes 1.33 seconds
```

Network restoration to recovery detection:

```text
204.49 seconds
= 3 minutes 24.49 seconds
```

## Monitoring Result

During the failure:

```text
service_status: DOWN
http_status: null
error: timed out
```

After recovery:

```text
service_status: UP
http_status: 200
response_time_ms: 144.47
```

## Findings

Nginx itself remained operational during the network block, but external HTTP monitoring detected the service as unavailable.

The failure mode differed from the Nginx service-stop test:

```text
Nginx stopped
→ Connection refused

TCP/80 network block
→ Connection timeout
```

This demonstrates that external monitoring can detect both service-level and network-level failures, while the observed error can help distinguish the failure type.
