# Phase 0 — Source Dataset Baseline Report

**Inventory Date:** 2026-09-14  
**Source Directory:** `/Users/deekshith/Downloads/Project 1/track2_cybersecurity_dataset_files`  
**Raw Source File Immutability:** Guaranteed (Read-Only Source Files)

---

## 1. Raw Dataset File Inventory

| File Name | Format | Record Count | File Size (Bytes) | Primary Key | SHA-256 Digest |
| :--- | :--- | ---: | ---: | :--- | :--- |
| `track2_firewall_logs.csv` | CSV | 30,600 | 3,938,382 | `log_id` | `1a2833a93832d53dd6c5e1204769bf1a72b0d5069d7ba17508fa6f11e381608c` |
| `track2_iam_audit_trail.json` | JSON | 20,500 | 9,266,351 | `event_id` | `316acf81d46734caa9fc8d9fe3c9794d9ae5aa6bc29782e2028a655b344fc687` |
| `track2_endpoint_alerts.xlsx` | XLSX | 8,240 | 1,039,504 | `alert_id` | `cd43513e3e6d3ed7ada3e6db884aaf5e2167668041e5d492ace799fa2a5e9f92` |
| `track2_identity_asset_master.csv` | CSV | 3,090 | 382,103 | `user_id` | `b5a70c3d4936857d8210fe098adcda78819d9e7465bdf8e635c5475ce1fab117` |
| `track2_dataset_notes.txt` | TXT | 61 lines | 2,416 | N/A | `f52b4a5dead99547c6270f3f76ea0a15c6ffb1b258e4fafe6d9c7c2702143ce3` |
| **Total Ingested Data Records** | | **62,430** | **14,626,340** | | |

---

## 2. Header & Schema Inventory

### `track2_firewall_logs.csv`
* **Columns (15):** `log_id`, `timestamp`, `hostname`, `src_ip`, `dst_ip`, `src_port`, `dst_port`, `protocol`, `action`, `bytes_sent`, `bytes_received`, `session_id`, `threat_flag`, `rule_name`, `geo_country`

### `track2_iam_audit_trail.json`
* **Keys (15):** `auth_method`, `department`, `device_id`, `event_id`, `event_type`, `failure_reason`, `geo_location`, `hostname`, `mfa_passed`, `risk_score`, `session_id`, `source_ip`, `timestamp`, `user_id`, `username`

### `track2_endpoint_alerts.xlsx`
* **Sheet Name:** `endpoint_alerts`
* **Columns (15):** `alert_id`, `detected_timestamp`, `resolved_timestamp`, `hostname`, `user_id`, `endpoint_product`, `alert_name`, `severity`, `status`, `description`, `file_path`, `process_name`, `sha256`, `assigned_to`, `device_criticality`

### `track2_identity_asset_master.csv`
* **Columns (12):** `user_id`, `username`, `full_name`, `department`, `role`, `location`, `hostname`, `device_id`, `status`, `hire_date`, `termination_date`, `manager_username`

---

## 3. Baseline Audit Directives

1. Raw dataset files under `track2_cybersecurity_dataset_files` are strictly immutable.
2. Ingestion iterations read directly from these raw files and write to isolated iteration output directories.
