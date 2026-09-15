# Phase 1 — Data Contract Specification

**Contract Version:** `1.0`  
**Scope:** Firewall Logs, IAM Audit Trail, Endpoint Alerts, Identity Asset Master

---

## 1. Field-Level Contract Matrix

### 1.1 Firewall Logs (`track2_firewall_logs.csv`)

| Field Name | Datatype | Required/Optional | Allowed Values | Normalization Rule | Validation Rule | Missing Valid? | Malformed Recoverable? | Quarantine On Error? | Security Sensitive? | Identity Resolution? | Detection? | Risk Scoring? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `log_id` | String | Required | Non-empty string | Strip whitespace | Unique non-empty string | No | No | Yes | No | No | No | No |
| `timestamp` | Datetime | Optional | ISO 8601, slash/dash formats, epoch | Parse to UTC datetime | Valid parseable datetime | Yes | No | Yes | Yes | No | Yes | Yes |
| `hostname` | String | Optional | Uppercase host, `.CORP.LOCAL` | Uppercase, replace `_` with `-`, strip suffix | Non-empty string | Yes | Yes | No | Yes | Yes | Yes | Yes |
| `src_ip` | String | Optional | Valid IPv4 address | Parse IPv4 structure | Valid IPv4 octet format (`0..255`) | Yes | No | Yes | Yes | Yes | Yes | Yes |
| `dst_ip` | String | Optional | Valid IPv4 address | Parse IPv4 structure | Valid IPv4 octet format (`0..255`) | Yes | No | Yes | Yes | Yes | Yes | Yes |
| `src_port` | Integer | Optional | `0..65535` | Integer conversion | `0 <= port <= 65535` | Yes | No | Yes | Yes | No | Yes | Yes |
| `dst_port` | Integer | Optional | `0..65535` | Integer conversion | `0 <= port <= 65535` | Yes | No | Yes | Yes | No | Yes | Yes |
| `protocol` | String | Optional | `tcp`, `udp`, `icmp`, `other` | Lowercase mapping (`6` $\rightarrow$ `tcp`, `17` $\rightarrow$ `udp`) | Known protocol string | Yes | Yes | No | Yes | No | Yes | Yes |
| `action` | String | Optional | `allow`, `deny`, `unknown` | Map permit/accept $\rightarrow$ `allow`; drop/block $\rightarrow$ `deny` | Standardized action category | Yes | Yes | No | Yes | No | Yes | Yes |
| `bytes_sent` | Integer | Optional | Non-negative integer | Decimal integer parsing | `bytes >= 0` | Yes | No | Yes | No | No | Yes | No |
| `bytes_received` | Integer | Optional | Non-negative integer | Decimal integer parsing | `bytes >= 0` | Yes | No | Yes | No | No | Yes | No |
| `session_id` | String | Optional | Non-empty string | Strip whitespace | Non-empty string | Yes | No | No | Yes | No | Yes | No |
| `threat_flag` | String | Optional | Boolean string | Normalize boolean | True/False boolean string | Yes | Yes | No | Yes | No | Yes | Yes |
| `rule_name` | String | Optional | Rule string | Strip whitespace | Text string | Yes | Yes | No | No | No | No | No |
| `geo_country` | String | Optional | Country code/name | Uppercase 2-letter ISO | String format | Yes | Yes | No | No | No | No | No |

---

### 1.2 IAM Audit Trail (`track2_iam_audit_trail.json`)

| Field Name | Datatype | Required/Optional | Allowed Values | Normalization Rule | Validation Rule | Missing Valid? | Malformed Recoverable? | Quarantine On Error? | Security Sensitive? | Identity Resolution? | Detection? | Risk Scoring? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | String | Required | Unique event identifier | Strip whitespace | Unique string | No | No | Yes | No | No | No | No |
| `timestamp` | Datetime | Optional | ISO 8601, slash/dash, epoch | Parse to UTC datetime | Valid parseable datetime | Yes | No | Yes | Yes | No | Yes | Yes |
| `user_id` | String | Optional | `EMP` + digits | Strip non-alphanumeric, prepend `EMP` if numeric | Valid `EMP\d+` pattern | Yes | Yes | Yes (if unrecognized) | Yes | Yes | Yes | Yes |
| `username` | String | Optional | User text handle | Lowercase string | Text handle | Yes | Yes | No | Yes | Yes | Yes | No |
| `department` | String | Optional | Department name | Canonical department mapping | Known canonical department | Yes | Yes | No | No | Yes | No | No |
| `source_ip` | String | Optional | Valid IPv4 address | Parse IPv4 structure | Valid IPv4 octet format (`0..255`) | Yes | No | Yes | Yes | Yes | Yes | Yes |
| `hostname` | String | Optional | Hostname string | Uppercase, replace `_` with `-`, strip suffix | Valid hostname string | Yes | Yes | No | Yes | Yes | Yes | Yes |
| `device_id` | String | Optional | Device identifier | Strip whitespace | Non-empty device string | Yes | Yes | No | Yes | Yes | No | No |
| `event_type` | String | Optional | Auth/admin event category | Canonical event type mapping | Standard event type | Yes | Yes | No | Yes | No | Yes | Yes |
| `mfa_passed` | Boolean | Optional | True/False boolean | Boolean conversion | Valid boolean value | Yes | Yes | No | Yes | No | Yes | Yes |
| `failure_reason` | String | Optional | Failure reason string | Lowercase text | Failure description | Yes | Yes | No | Yes | No | Yes | No |
| `risk_score` | Float | Optional | Numeric `0.0..100.0` | Parse float, strip `/100` | `0.0 <= score <= 100.0` | Yes | No | Yes | Yes | No | Yes | Yes |
| `session_id` | String | Optional | Session string | Strip whitespace | Non-empty string | Yes | No | No | Yes | No | Yes | No |

---

### 1.3 Endpoint Alerts (`track2_endpoint_alerts.xlsx`)

| Field Name | Datatype | Required/Optional | Allowed Values | Normalization Rule | Validation Rule | Missing Valid? | Malformed Recoverable? | Quarantine On Error? | Security Sensitive? | Identity Resolution? | Detection? | Risk Scoring? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `alert_id` | String | Required | Unique alert identifier | Strip whitespace | Unique string | No | No | Yes | No | No | No | No |
| `detected_timestamp` | Datetime | Optional | Multi-format timestamp | Parse to UTC datetime | Valid parseable datetime | Yes | No | Yes | Yes | No | Yes | Yes |
| `resolved_timestamp` | Datetime | Optional | Multi-format timestamp | Parse to UTC datetime | `resolved >= detected` | Yes | No | Yes (if before detected) | Yes | No | Yes | No |
| `hostname` | String | Optional | Endpoint hostname | Uppercase, strip suffix | Valid hostname string | Yes | Yes | No | Yes | Yes | Yes | Yes |
| `user_id` | String | Optional | `EMP` + digits | Canonical employee ID mapping | Valid `EMP\d+` pattern | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `alert_name` | String | Optional | Threat alert name | Strip whitespace | Text string | Yes | Yes | No | Yes | No | Yes | Yes |
| `severity` | String | Optional | `low`, `medium`, `high`, `critical` | Lowercase string | Valid severity string | Yes | Yes | No | Yes | No | Yes | Yes |
| `sha256` | String | Optional | 64-char hex string | Lowercase string | `^[0-9a-fA-F]{64}$` | Yes | No | Yes | Yes | No | Yes | Yes |
| `device_criticality` | String | Optional | Criticality label | Lowercase string | Valid label | Yes | Yes | No | Yes | No | No | Yes |

---

### 1.4 Identity Asset Master (`track2_identity_asset_master.csv`)

| Field Name | Datatype | Required/Optional | Allowed Values | Normalization Rule | Validation Rule | Missing Valid? | Malformed Recoverable? | Quarantine On Error? | Security Sensitive? | Identity Resolution? | Detection? | Risk Scoring? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `user_id` | String | Required | `EMP` + digits | Primary identity key normalization | Valid `EMP\d+` pattern | No | Yes | Yes | Yes | Yes | Yes | Yes |
| `username` | String | Optional | Username handle | Lowercase string | User handle | Yes | Yes | No | Yes | Yes | No | No |
| `full_name` | String | Optional | Person full name | Titlecase string | Name text | Yes | Yes | No | No | No | No | No |
| `department` | String | Optional | Department name | Canonical department mapping | Standard department | Yes | Yes | No | No | Yes | No | No |
| `role` | String | Optional | Organizational role | Lowercase text | Role text | Yes | Yes | No | No | No | No | No |
| `hostname` | String | Optional | Master host assignment | Uppercase hostname | Host string | Yes | Yes | No | Yes | Yes | No | No |
| `device_id` | String | Optional | Device identifier | Strip whitespace | Device string | Yes | Yes | No | Yes | Yes | No | No |
