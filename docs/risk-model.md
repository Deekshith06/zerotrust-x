# Risk model

Risk is deterministic and bounded to 0–100. Current evidence contributions include authentication failures, endpoint alerts, denied network actions, and rule detections. Each user result includes level, reason codes, and evidence event IDs.

The model is explainable and reproducible but not calibrated against verified incident labels. The synthetic dataset cannot support precision, recall, insider-threat accuracy, or malicious-intent claims. Future calibration must use analyst-reviewed or independently verified labels and preserve model/rule versioning.

The score is a prioritization signal, not a verified threat label. It is never assigned or modified by an LLM. Source `risk_score` values remain telemetry and are not ground truth. The optional grounded investigation workflow may summarize returned evidence but cannot change severity or risk.
