# ZeroTrust-X Frontend Architecture & Design System Specification

## 1. Executive Summary & Design Principles

ZeroTrust-X is an evidence-led cybersecurity operations workspace built for synthetic Track 2 enterprise telemetry (IAM, endpoint, firewall, identity). It replaces generic SaaS/AI templates with an industrial, quiet, and high-density analyst workstation designed for prolonged SOC shifts.

### Core Principles
1. **Evidence-Centricity**: "Every pixel represents evidence." Every score, alert, graph node, and agent claim links to deterministic underlying records in immutable Parquet artifacts (`events.parquet`, `detections.parquet`, `user_risk.parquet`).
2. **Quiet Operational Density**: Restrained typography, structured panels, split views, and deep data grids replace fluffy cards, decorative neon gradients, and cartoon AI mascots.
3. **Strict Zero-Guess Geolocation Policy**: Country intelligence is derived exclusively from explicit `geo_country` telemetry or structured, documented GeoIP provider abstractions (`GeoIPProvider`). If telemetry lacks country data, it is displayed as `UNKNOWN / UNRESOLVED`. The platform never guesses or fabricates locations from raw IP addresses.
4. **Investigation-First UX**: Analysts do not jump between disjointed CRUD pages. Selecting an identity, an alert, or a country transitions the unified workstation into contextual case triage (`Country → IP → User → Device → Session → Events → Alert → Investigation`).
5. **Grounded Agent Boundary**: The AI SOC Investigator is an investigative copilot, not a generic chatbot. It executes a 4-step pipeline (`intake → evidence collection → correlation → report validation`), cites exact IDs, verifies citations, and surfaces data quality warnings rather than hallucinating confidence numbers.

---

## 2. Layout System & Surface Hierarchy

The interface implements a multi-layered workspace structure that adapts dynamically to the active investigation context:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ GLOBAL COMMAND BAR (Brand · Omnibar Search · Tenant · System Posture · Role) │
├──────────────┬──────────────────────────────────────────────┬───────────────┤
│              │                                              │               │
│ CONTEXT RAIL │            PRIMARY WORKSPACE                 │ INSIGHT RAIL  │
│              │                                              │               │
│ Navigation   │ [ Threat Landscape / Investigation / Graph / │ Entity        │
│ Shortcuts    │   Country Intelligence / Agent / Quality ]   │ Inspector     │
│ System state │                                              │ Citations     │
│              │                                              │ Live Notes    │
│              │                                              │               │
├──────────────┴──────────────────────────────────────────────┴───────────────┤
│ PERSISTENT ACTIVITY STRIP (Status · Grounding · GeoIP State · ShortKeys)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Layout Modes
- **Threat Landscape / Dashboard**: Wide multi-pane operational overview combining system readiness, bounded filters, open detection queue, risk distribution, and geographic preview.
- **Investigation Workspace**: Flagship 3-pane layout: Entity Context (left), Vertical Evidence Timeline & Signal Inspection (center), and Insight Rail with Analyst Scratchpad (right).
- **Security Graph Explorer**: Pan-and-zoom SVG canvas with type filtering, progressive node expansion, and contextual Entity Inspector.
- **AI SOC Investigator**: 3-pane layout with Investigation Context, Grounded Conversation Stream with Suggested Analytical Actions, and Evidence Tool Verification pipeline.
- **Global Country Intelligence**: Split-screen with interactive SVG World Map, Activity Concentration, and deep-dive drill-down drawer.
- **Data Quality Register**: Full-width diagnostic suite breaking down findings vs affected rows across sources and reason codes.
- **Employee Portal**: Calm, clean corporate interface for self-scoped activity inspection.
- **Demo Scenario Lab**: Dedicated control console for deterministic attack chain demonstrations.

---

## 3. Design Tokens: Color, Typography, & Radius

### Color System (Dual-Theme: Dark Operations First & Light Operations)

| Token Name | Dark Operations (Default) | Light Operations | Usage |
|---|---|---|---|
| `--bg` | `#07090b` | `#f4f6f8` | Root background |
| `--surface-0` | `#0a0e12` | `#eaedf1` | Navigation rails & command bar |
| `--surface-1` | `#0f141a` | `#ffffff` | Primary workspace panels & tables |
| `--surface-2` | `#151b22` | `#f6f8fa` | Elevated cards, inspectors, modal surfaces |
| `--surface-3` | `#1c242e` | `#eceff3` | Active rows, hovered items, toolbar inputs |
| `--line-dim` | `#1c232d` | `#dfe3e8` | Dividers and subtle separators |
| `--line-base` | `#27323e` | `#cbd2dc` | Primary panel borders |
| `--line-strong`| `#3c4c5e` | `#9ba8b8` | Focus rings and active borders |
| `--ink` | `#e6ecf2` | `#121820` | Primary high-contrast typography |
| `--muted` | `#93a1b0` | `#586574` | Secondary labels, descriptions |
| `--dim` | `#5a6877` | `#8c99a8` | Timestamps, metadata, subtle captions |

### Restrained Semantic Palette
Semantic states always combine color with an explicit text label and structural shape/icon:

- **CRITICAL** (`◆` Diamond / Red): Color `#e05252`, Dark surface `#241214`, Border `#522025`.
- **HIGH** (`▲` Triangle / Amber): Color `#e27e36`, Dark surface `#26160e`, Border `#562914`.
- **WARNING / MEDIUM** (`⬡` Hexagon / Ochre): Color `#d4a34b`, Dark surface `#241d10`, Border `#4e3b18`.
- **LOW / INFO** (`●` Circle / Steel Blue): Color `#629ee8`, Dark surface `#121e2d`, Border `#1e3858`.
- **NORMAL / HEALTHY** (`✓` Check / Sage Green): Color `#52b788`, Dark surface `#10241b`, Border `#1c4431`.
- **EVIDENCE ACCENT** (`◉` Target / Cadet Teal): Color `#60c4cf`, Dark surface `#0f2328`, Border `#1a454d`.
- **UNRESOLVED / UNKNOWN** (`◌` Ring / Slate): Color `#7f8c9b`, Dark surface `#161a20`, Border `#2d3542`.

### Typography
- **Technical Monospace**: `ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace` applied to event IDs, hashes, timestamps, IP addresses, ports, risk scores, and citations.
- **Interface Sans**: `Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` for navigation, headings, and labels.
- **Scale**:
  - `font-size: 10px`: Eyebrows, micro badges, tabular notes (`letter-spacing: 0.08em; text-transform: uppercase`)
  - `font-size: 11px`: Metadata, timestamps, toolbar buttons, secondary text
  - `font-size: 12px`: Table body, inspector key-value items, description text
  - `font-size: 13px`: Base interface text, form controls, signal titles
  - `font-size: 14px`: Section headers, modal titles, panel titles
  - `font-size: 20px` - `24px`: Key numeric metrics and view titles

### Geometry & Radius
- Sharp, industrial precision: `border-radius: 2px` to `4px`.
- No large pill-shaped containers or bubbly modern card radiuses.
- Crisp 1px solid borders (`var(--line-base)`).

---

## 4. Navigation Model & Keyboard Shortcuts

Global Omnibar search with live type tags supports instant lookup across:
- `USER` (e.g. `EMP10001`, `EMP11411`)
- `DEVICE` (e.g. `DEV10001`, `DEV77305`)
- `IP` (e.g. `203.0.113.45`, `192.168.1.1`)
- `ALERT` (e.g. `det-failed-EMP11411`, `MULTIPLE_FAILED_LOGINS`)
- `EVENT` (e.g. `IAM00013267`, `EPA00001579`)
- `COUNTRY` (e.g. `India`, `United States`, `China`, `Russia`)

### Keyboard Shortcuts
- `/` or `Ctrl/Cmd + K`: Focus Omnibar search
- `g d`: Navigate to SOC Threat Landscape Overview
- `g i`: Navigate to Investigation Workspace
- `g t`: Navigate to Evidence Timeline
- `g g`: Navigate to Entity Relationship Graph
- `g c`: Navigate to Country Threat Intelligence
- `g a`: Navigate to AI SOC Investigator
- `g q`: Navigate to Data Quality Register
- `g s`: Navigate to Demo / Scenario Lab
- `g e`: Navigate to Employee Self-Scope Portal
- `t`: Toggle Dark / Light Operations Mode
- `?`: Open Keyboard Shortcut & Command Palette modal

---

## 5. Flagship Investigation Model

The Investigation Workspace (`/soc/investigations/:id`) is designed as an analytical triage desk:
1. **Entity Context**: Identity details, department, deterministic 0–100 risk score, contributing reason codes, assigned assets, and source IP addresses.
2. **Timeline Evidence**: Chronological multi-source events with source tags (IAM, Endpoint, Firewall, Identity), action tags, and severity badges.
3. **Signal Inspector Drawer**: Clicking any event displays full canonical fields, raw payload, ingestion source path, row number, and SHA-256 hash.
4. **Analyst Actions**:
   - Mark evidence as relevant (adds to investigation evidence set).
   - Reject irrelevant telemetry.
   - Add analyst scratchpad notes (persisted in session storage).
   - Change investigation lifecycle status (`OPEN`, `UNDER_ANALYSIS`, `ESCALATED`, `RESOLVED`).
   - Deep-link to Entity Graph (`Explore In Graph`).
   - Deep-link to AI SOC Investigator (`Ask AI Investigator`).

---

## 6. Interactive Security Graph Model

The relationship graph renders deterministic, bounded nodes and edges extracted from event evidence:
- **USER** (Circle)
- **DEVICE** (Square)
- **HOSTNAME** (Rounded Square)
- **IP** (Diamond)
- **SESSION** (Rounded Rectangle)
- **ALERT** (Hexagon)
- **EVENT** (Small Dot)
- **COUNTRY** (Large Geographic Node)
- **NETWORK DESTINATION** (Diamond)

### Controls & Actions
- Pan, zoom (`+`, `-`), fit-to-view, and reset buttons.
- Filter toggle by entity type (show/hide alerts, IPs, devices, sessions, events, countries).
- Selection inspector displaying properties, event counts, and related nodes.
- **Action**: `[ INVESTIGATE THIS PATH ]` transitions directly into the Investigation Workspace with the target entity loaded.

---

## 7. Country Threat Intelligence & Drill-Down Architecture

### GeoIP Policy & Grounding
- **Explicit Telemetry First**: The dataset's canonical `geo_country` field is authoritative.
- **Strict No-Inference**: ZeroTrust-X strictly prohibits geolocation guessing from raw IP strings.
- **Graceful Unresolved State**: Any record lacking country data is classified as `UNKNOWN / UNRESOLVED`.
- **Enrichment Provider**: `GeoIPProvider` interface (`src/zerotrust_x/geoip.py`). If offline, status displays `Geo enrichment unavailable` without blocking SOC analysts.

### Full Analytical Drill-Down
```text
Country (e.g. IN / India)
  └── IPs (e.g. 203.0.113.45)
        └── Users (e.g. EMP11411 · Risk 100)
              └── Devices (e.g. DEV77305)
                    └── Sessions (e.g. SID970652)
                          └── Events (24 failed auths, MFA failure)
                                └── Alerts (MULTIPLE_FAILED_LOGINS, MFA_FAILURE)
                                      └── [ INVESTIGATE IN WORKSPACE ]
```

---

## 8. AI SOC Investigator Experience

The AI SOC Investigator copilot provides grounded investigative assistance:
- **Hypothesis Display**: Contextual hypothesis dynamically formulated based on the analyst's question.
- **Evidence Traceability**: Every statement cites verified IDs (`IAM...`, `EPA...`, `FW...`). Clicking citations opens the original event metadata.
- **Tool Pipeline**: Live verification status (`query_user ✓`, `query_timeline ✓`, `query_detections ✓`, `query_graph ✓`, `verify_citations ✓`).
- **Safety & Quality Alerts**: Proactively warns the analyst when IP validation was flagged in quarantine or when GeoIP enrichment is unavailable.
- **Contextual Suggestions**: Single-click analytical prompts:
  - "Why is this user high risk?"
  - "Explain this risk score"
  - "Show the attack timeline"
  - "Find related devices"
  - "Find related IPs"
  - "Compare with peer behavior"
  - "Explain why this alert fired"
  - "Find supporting evidence"
  - "Find contradictory evidence"
  - "Summarize this investigation"

---

## 9. Data Quality Register & Explanation

Displays the immutable frozen data quality baseline:
- Total Ingested Records: **62,430**
- Quarantined Findings: **36,220**
- Affected Rows: **29,536**
- Duplicate Records: **1,430**
- Finding-to-Row Ratio: **1.2263**
- Cleaning Status: **CLEAN_WITH_DOCUMENTED_EXCEPTIONS**

### Educational Distinction
Explains why finding count (36,220) exceeds affected rows (29,536): multi-field validation findings on single records (e.g. invalid IP address combined with out-of-range port) produce separate reason-coded findings while preserving the row's lineage.

---

## 10. Demo Scenario Lab & Live Attack Chains

Provides a discreet, professional scenario console with 5 deterministic scenarios mapped to actual dataset entities:
1. `Normal Employee Login` (`EMP10001` · Risk 10 · Low)
2. `Account Credential Stuffing` (`EMP10522` · Risk 92 · Critical)
3. `MFA Fatigue & Token Bypass` (`EMP11411` · Risk 94 · Critical)
4. `Endpoint EDR Threat & Egress` (`EMP10892` · Risk 88 · High)
5. `Multi-Source Correlated Incident` (`EMP11411` · Risk 100 · Critical)

Provides step-by-step playback with simulated time offsets and direct deep-linking into the live SOC investigation workspace.
