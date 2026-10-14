# Incident Test 03 - HTTP Health Endpoint Failure

## Purpose

Webサーバーおよびネットワークは正常な状態を維持したまま、
監視対象の `/health` エンドポイントのみを利用不能にし、
HTTP外形監視がHTTPレベルの異常を検知できることを確認する。

## Environment

- Target: Sakura VPS / Rocky Linux
- Web server: Nginx
- Monitoring: Python HTTP health check
- Scheduler: systemd timer
- Monitoring interval: 5 minutes
- Health endpoint: `/health`

## Test Procedure

1. Nginxがactiveであることを確認
2. `/` がHTTP 200を返すことを確認
3. `/health` ファイルを削除
4. systemd timerによる外形監視でDOWNを検知
5. Ansible Playbookで `/health` を復旧
6. systemd timerによる外形監視でHTTP 200への正常復帰を確認

## Result

| Event | Time (UTC) | HTTP Status | Response Time |
|---|---|---:|---:|
| Normal state | 2026-10-14 13:06:23 | 200 | 169.00 ms |
| Health endpoint removed | 2026-10-14 13:11:53 | - | - |
| Failure detected | 2026-10-14 13:12:23 | 404 | 173.65 ms |
| Health endpoint restored | 2026-10-14 13:17:34 | - | - |
| Recovery detected | 2026-10-14 13:18:23 | 200 | 161.33 ms |

### Failure detection time

```text
30.39 seconds
```

### Recovery detection time

```text
48.77 seconds
```

## Monitoring Result

Before the failure:

```text
service_status: UP
http_status: 200
response_time_ms: 169.00
```

During the failure:

```text
service_status: DOWN
http_status: 404
response_time_ms: 173.65
error: HTTP Error 404: Not Found
```

After recovery:

```text
service_status: UP
http_status: 200
response_time_ms: 161.33
```

## Findings

The monitoring system detected an HTTP-level failure while the Nginx
service and network connectivity remained operational.

Unlike a service-stop or network-block failure, the HTTP server still
responded normally at the transport level. However, the monitored
endpoint returned HTTP 404, allowing the health check to classify the
service as DOWN.

The three incident tests represent different failure modes:

```text
Test 01: Nginx service stopped
→ Connection refused

Test 02: TCP/80 network blocked
→ Connection timeout

Test 03: Health endpoint unavailable
→ HTTP 404 Not Found
```

This demonstrates that the external monitoring mechanism can distinguish
between service-level, network-level, and HTTP-level failures based on
the observed response.

Monitoring runs every five minutes, so detection time depends on when
the failure occurs relative to the next timer execution. In this test,
the HTTP failure was detected after 30.39 seconds and recovery was
detected after 48.77 seconds.
