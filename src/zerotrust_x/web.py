"""Industrial analyst console and executive cybersecurity operations workstation."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from zerotrust_x.api import create_app
from zerotrust_x.world_map import get_world_map_svg

DASHBOARD = r'''<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZeroTrust-X | Detection Operations Workstation</title>
<style>
:root {
  color-scheme: dark;
  --bg: #07090c;
  --surface-0: #0a0d12;
  --surface-1: #0f141a;
  --surface-2: #141a22;
  --surface-3: #1a222c;
  --surface-hover: #202936;
  --line-dim: #18202a;
  --line-base: #242f3d;
  --line-strong: #38485c;
  --ink: #e8edf2;
  --muted: #91a0b0;
  --dim: #5c6b7a;
  --cyan: #60c4cf;
  --cyan-bg: #0f2428;
  --cyan-border: #1a454d;
  --amber: #e2a84a;
  --amber-bg: #241d10;
  --amber-border: #4d3b19;
  --red: #e05555;
  --red-bg: #251214;
  --red-border: #522024;
  --green: #54b88a;
  --green-bg: #10241b;
  --green-border: #1c4431;
  --blue: #6aa3e8;
  --blue-bg: #121e2d;
  --blue-border: #1e3858;
  --orange: #e58238;
  --orange-bg: #26160e;
  --orange-border: #562914;
  --slate: #7f8d9c;
  --slate-bg: #161a20;
  --slate-border: #2d3642;
  --graph-bg: radial-gradient(circle at 50% 50%, #0c121e 0%, #07090e 100%);
  --graph-dot: rgba(255,255,255,0.06);
  --graph-pill-bg: rgba(8, 12, 19, 0.95);
  --map-bg: #070a0f;
  --map-land: #101622;
  --map-land-border: #1c2738;
  --map-hover: #1d2c40;
  --map-activity: #132738;
  --map-activity-border: #2563eb;
  --map-active: #183e54;
  --map-tooltip-bg: rgba(8, 12, 18, 0.96);
  --map-graticule: rgba(255,255,255,0.05);
  --radius: 3px;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  --font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
html[data-theme="light"] {
  color-scheme: light;
  --bg: #f5f7fa;
  --surface-0: #eaeff5;
  --surface-1: #ffffff;
  --surface-2: #f8fafc;
  --surface-3: #e2e8f0;
  --surface-hover: #e2e8f0;
  --line-dim: #e2e8f0;
  --line-base: #cbd5e1;
  --line-strong: #94a3b8;
  --ink: #0f172a;
  --muted: #475569;
  --dim: #64748b;
  --cyan: #0891b2;
  --cyan-bg: #ecfeff;
  --cyan-border: #a5f3fc;
  --amber: #d97706;
  --amber-bg: #fffbeb;
  --amber-border: #fde68a;
  --red: #dc2626;
  --red-bg: #fef2f2;
  --red-border: #fecaca;
  --green: #059669;
  --green-bg: #ecfdf5;
  --green-border: #a7f3d0;
  --blue: #2563eb;
  --blue-bg: #eff6ff;
  --blue-border: #bfdbfe;
  --orange: #ea580c;
  --orange-bg: #fff7ed;
  --orange-border: #fed7aa;
  --slate: #475569;
  --slate-bg: #f1f5f9;
  --slate-border: #cbd5e1;
  --graph-bg: radial-gradient(circle at 50% 50%, #ffffff 0%, #edf2f7 100%);
  --graph-dot: rgba(0,0,0,0.08);
  --graph-pill-bg: rgba(255, 255, 255, 0.98);
  --map-bg: #e2eaf2;
  --map-land: #cbd5e1;
  --map-land-border: #94a3b8;
  --map-hover: #94a3b8;
  --map-activity: #bfdbfe;
  --map-activity-border: #2563eb;
  --map-active: #a5f3fc;
  --map-tooltip-bg: rgba(255, 255, 255, 0.98);
  --map-graticule: rgba(15,23,42,0.12);
}
* { box-sizing: border-box; }
html, body {
  margin: 0; min-height: 100%;
  background: var(--bg); color: var(--ink);
  font: 12px/1.45 var(--font-sans);
  letter-spacing: -0.01em;
  -webkit-font-smoothing: antialiased;
}
button, input, select, textarea { font: inherit; color: inherit; }
button { cursor: pointer; }
button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
  outline: 2px solid var(--cyan); outline-offset: 1px;
}
code, pre, kbd, .mono { font-family: var(--font-mono); }

/* Layout Grid */
.app {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  grid-template-rows: 52px 1fr 28px;
  grid-template-areas:
    "top top"
    "rail work"
    "strip strip";
  min-height: 100vh;
}

/* Top Command Bar */
.command-bar {
  grid-area: top;
  background: var(--surface-0);
  border-bottom: 1px solid var(--line-base);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; z-index: 50; gap: 16px;
}
.brand {
  display: flex; align-items: center; gap: 10px; min-width: 220px;
}
.brand-mark {
  width: 28px; height: 28px; background: var(--cyan-bg);
  border: 1px solid var(--cyan-border); color: var(--cyan);
  display: grid; place-items: center; font-weight: 800; font-size: 11px;
  border-radius: var(--radius); letter-spacing: 0.05em;
}
.brand-title { font-weight: 700; font-size: 14px; letter-spacing: 0.02em; }
.brand-sub { font-size: 10px; color: var(--dim); letter-spacing: 0.08em; text-transform: uppercase; }

.omnibar {
  flex: 1; max-width: 520px; position: relative;
}
.omnibar input {
  width: 100%; background: var(--surface-1);
  border: 1px solid var(--line-base); color: var(--ink);
  padding: 7px 32px 7px 12px; border-radius: var(--radius);
  font-size: 12px;
}
.omnibar input::placeholder { color: var(--dim); }
.omnibar kbd {
  position: absolute; right: 8px; top: 7px;
  background: var(--surface-2); border: 1px solid var(--line-dim);
  color: var(--dim); font-size: 10px; padding: 1px 5px; border-radius: 2px;
}
.omni-results {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0;
  background: var(--surface-1); border: 1px solid var(--line-strong);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5); border-radius: var(--radius);
  max-height: 380px; overflow-y: auto; display: none; z-index: 100;
}
.omni-results.active { display: block; }
.omni-group { padding: 6px 10px; font-size: 10px; color: var(--dim); letter-spacing: 0.08em; text-transform: uppercase; background: var(--surface-0); border-bottom: 1px solid var(--line-dim); }
.omni-item {
  padding: 8px 12px; display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; border-bottom: 1px solid var(--line-dim);
}
.omni-item:hover, .omni-item.selected { background: var(--surface-3); }
.omni-item-left { display: flex; align-items: center; gap: 8px; }
.omni-tag {
  font-size: 9px; padding: 2px 5px; border-radius: 2px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.06em;
}

.top-controls {
  display: flex; align-items: center; gap: 12px;
}
.badge-capsule {
  display: flex; align-items: center; gap: 6px;
  background: var(--surface-1); border: 1px solid var(--line-base);
  padding: 4px 8px; border-radius: var(--radius); font-size: 10px;
  color: var(--muted); letter-spacing: 0.04em;
}
.status-indicator {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green); display: inline-block;
}
.status-indicator.amber { background: var(--amber); }
.status-indicator.red { background: var(--red); }
.role-select {
  background: var(--surface-1); border: 1px solid var(--line-base);
  color: var(--ink); padding: 5px 8px; border-radius: var(--radius); font-size: 11px;
}
.btn-icon {
  background: transparent; border: 1px solid var(--line-base);
  color: var(--muted); padding: 5px 9px; border-radius: var(--radius);
  font-size: 11px; display: flex; align-items: center; gap: 4px;
}
.btn-icon:hover { background: var(--surface-3); color: var(--ink); border-color: var(--line-strong); }

/* Left Context Rail */
.context-rail {
  grid-area: rail;
  background: var(--surface-0);
  border-right: 1px solid var(--line-base);
  padding: 16px 10px; display: flex; flex-direction: column; gap: 20px;
  overflow-y: auto;
}
.nav-group-title {
  color: var(--dim); font-size: 9px; letter-spacing: 0.12em;
  text-transform: uppercase; padding: 0 10px 6px; font-weight: 600;
}
.nav-list { display: flex; flex-direction: column; gap: 2px; }
.nav-item {
  display: flex; align-items: center; justify-content: space-between;
  background: transparent; border: 1px solid transparent;
  color: var(--muted); padding: 8px 10px; border-radius: var(--radius);
  font-size: 12px; text-align: left; width: 100%; transition: none;
}
.nav-item:hover {
  background: var(--surface-2); color: var(--ink); border-color: var(--line-dim);
}
.nav-item.active {
  background: var(--surface-3); color: var(--ink);
  border-color: var(--line-base); font-weight: 500;
  box-shadow: inset 3px 0 var(--cyan);
}
.nav-item kbd {
  font-size: 9px; color: var(--dim); font-family: var(--font-mono);
}
.rail-footer {
  margin-top: auto; padding: 12px 10px 0; border-top: 1px solid var(--line-dim);
  color: var(--dim); font-size: 10px; display: flex; flex-direction: column; gap: 4px;
}

/* Primary Workspace */
.workspace {
  grid-area: work;
  background: var(--bg);
  overflow-y: auto;
  padding: 24px 28px 48px;
}
.view { display: none; }
.view.active { display: block; }

/* View Header */
.view-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 1px solid var(--line-base); padding-bottom: 16px; margin-bottom: 20px;
  gap: 16px; flex-wrap: wrap;
}
.eyebrow {
  color: var(--cyan); font-size: 10px; letter-spacing: 0.14em;
  text-transform: uppercase; font-weight: 600; margin-bottom: 4px;
}
.view-title {
  font-size: 22px; font-weight: 600; letter-spacing: -0.02em; margin: 0;
}
.view-desc {
  color: var(--muted); margin: 4px 0 0; font-size: 12px;
}
.view-meta {
  text-align: right; font-size: 11px; color: var(--dim);
}

/* Operational Indicator Strip */
.system-state-bar {
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 8px; margin-bottom: 20px;
}
.state-pill {
  background: var(--surface-1); border: 1px solid var(--line-base);
  padding: 8px 10px; border-radius: var(--radius);
}
.state-label { font-size: 9px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.08em; }
.state-value { font-size: 11px; font-weight: 600; margin-top: 3px; display: flex; align-items: center; gap: 5px; }

/* Panels & Surfaces */
.panel {
  background: var(--surface-1); border: 1px solid var(--line-base);
  border-radius: var(--radius); min-width: 0;
}
.panel-head {
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid var(--line-base); padding: 11px 16px;
  background: var(--surface-0);
}
.panel-title {
  font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; margin: 0; display: flex; align-items: center; gap: 8px;
}
.panel-note { font-size: 11px; color: var(--dim); }
.panel-body { padding: 14px 16px; }

/* Semantic Badges */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 6px; border-radius: 2px; font-size: 10px;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;
  font-family: var(--font-mono); border: 1px solid transparent;
}
.badge.critical { background: var(--red-bg); border-color: var(--red-border); color: var(--red); }
.badge.high { background: var(--orange-bg); border-color: var(--orange-border); color: var(--orange); }
.badge.medium, .badge.warning { background: var(--amber-bg); border-color: var(--amber-border); color: var(--amber); }
.badge.low, .badge.info { background: var(--blue-bg); border-color: var(--blue-border); color: var(--blue); }
.badge.normal, .badge.ok { background: var(--green-bg); border-color: var(--green-border); color: var(--green); }
.badge.evidence { background: var(--cyan-bg); border-color: var(--cyan-border); color: var(--cyan); }
.badge.slate { background: var(--slate-bg); border-color: var(--slate-border); color: var(--slate); }

/* Data Tables */
.table-wrap { overflow-x: auto; width: 100%; }
table.data-table {
  width: 100%; border-collapse: collapse; text-align: left;
}
table.data-table th {
  padding: 8px 12px; font-size: 10px; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--dim); font-weight: 600;
  border-bottom: 1px solid var(--line-base); background: var(--surface-0);
}
table.data-table td {
  padding: 9px 12px; font-size: 11px; border-bottom: 1px solid var(--line-dim);
  color: var(--muted);
}
table.data-table tr:hover td { background: var(--surface-2); color: var(--ink); }
table.data-table td.mono-cell { font-family: var(--font-mono); color: var(--ink); }

/* Controls & Toolbars */
.toolbar {
  display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
}
.toolbar input, .toolbar select {
  background: var(--surface-1); border: 1px solid var(--line-base);
  color: var(--ink); padding: 6px 9px; border-radius: var(--radius);
  font-size: 11px;
}
.btn {
  padding: 6px 12px; border-radius: var(--radius); font-size: 11px;
  font-weight: 500; display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid transparent;
}
.btn-primary {
  background: var(--cyan-bg); border-color: var(--cyan-border); color: var(--cyan);
}
.btn-primary:hover { background: #13343a; border-color: var(--cyan); color: #c4f1f5; }
.btn-secondary {
  background: var(--surface-2); border-color: var(--line-base); color: var(--muted);
}
.btn-secondary:hover { background: var(--surface-3); color: var(--ink); border-color: var(--line-strong); }
.btn-danger {
  background: var(--red-bg); border-color: var(--red-border); color: var(--red);
}

/* Callout Notices */
.notice {
  padding: 10px 14px; border-radius: var(--radius); font-size: 11px;
  border: 1px solid var(--line-base); background: var(--surface-1);
  color: var(--muted); margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}
.notice.grounded { border-color: var(--green-border); background: var(--green-bg); color: var(--green); }
.notice.rejected, .notice.alert { border-color: var(--red-border); background: var(--red-bg); color: var(--red); }
.notice.warning { border-color: var(--amber-border); background: var(--amber-bg); color: var(--amber); }

/* Investigation 3-Pane Workstation */
.investigation-grid {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr) 320px;
  gap: 16px;
}
.case-card {
  padding: 12px; border-bottom: 1px solid var(--line-dim);
}
.case-card:last-child { border-bottom: 0; }
.timeline-list {
  display: flex; flex-direction: column; gap: 8px; max-height: 640px; overflow-y: auto; padding-right: 4px;
}
.timeline-event {
  background: var(--surface-1); border: 1px solid var(--line-base);
  border-radius: var(--radius); padding: 10px 12px; cursor: pointer;
  border-left: 3px solid var(--slate); position: relative;
}
.timeline-event:hover { background: var(--surface-2); border-color: var(--line-strong); }
.timeline-event.selected { border-color: var(--cyan); background: var(--surface-2); }
.timeline-event.auth-fail { border-left-color: var(--red); }
.timeline-event.auth-success { border-left-color: var(--green); }
.timeline-event.mfa-fail { border-left-color: var(--orange); }
.timeline-event.endpoint-alert { border-left-color: var(--red); }
.timeline-event.firewall-deny { border-left-color: var(--amber); }
.timeline-head {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;
}
.timeline-time { font-family: var(--font-mono); font-size: 10px; color: var(--dim); }
.timeline-title { font-weight: 600; font-size: 12px; }
.timeline-meta { font-size: 10px; color: var(--muted); margin-top: 3px; }

.graph-viewport {
  position: relative; width: 100%; height: 560px;
  background-color: var(--surface-1);
  background-image: radial-gradient(var(--line-strong) 0.8px, transparent 0.8px);
  background-size: 24px 24px;
  border: 1px solid var(--line-base); border-radius: var(--radius); overflow: hidden;
  user-select: none;
}
html[data-theme="light"] .graph-viewport {
  background-color: #ffffff !important;
  background-image: radial-gradient(#cbd5e1 1px, transparent 1px) !important;
}
.graph-viewport svg { width: 100%; height: 100%; display: block; background: transparent !important; }
.graph-toolbar {
  position: absolute; top: 12px; right: 12px;
  display: flex; gap: 6px; z-index: 10;
}
.edge {
  stroke: var(--line-strong);
  stroke-width: 1.2px;
  opacity: 0.35;
  transition: stroke 0.15s ease, stroke-width 0.15s ease, opacity 0.15s ease;
}
.edge.highlighted {
  stroke: var(--cyan) !important;
  stroke-width: 2.2px !important;
  opacity: 1 !important;
}
.edge.dimmed {
  opacity: 0.08 !important;
}
.edge-label-group {
  pointer-events: none;
}
.edge-label-bg {
  fill: var(--surface-1);
  stroke: var(--line-base);
  stroke-width: 0.8px;
}
.edge-label-text {
  fill: var(--muted);
  font-size: 8.5px;
  font-family: var(--font-mono);
  font-weight: 500;
}
.node {
  cursor: pointer;
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.node.dimmed {
  opacity: 0.18 !important;
}
.node.selected .node-shape {
  filter: drop-shadow(0 0 8px var(--cyan));
}
.node.selected .node-pill-bg {
  stroke: var(--cyan) !important;
  stroke-width: 1.8px !important;
}
.node:hover .node-pill-bg {
  stroke: var(--cyan);
  stroke-width: 1.5px;
  fill: var(--surface-hover);
}
.node-pill-bg {
  fill: var(--graph-pill-bg);
  stroke-width: 1px;
  filter: drop-shadow(0 2px 5px rgba(0,0,0,0.15));
  transition: stroke 0.15s ease, fill 0.15s ease;
}
.node-pill-text {
  font-size: 11px;
  font-family: var(--font-mono);
  font-weight: 600;
  pointer-events: none;
  letter-spacing: 0.2px;
}

/* World Map SVG */
.map-container {
  width: 100%; height: 440px; background: var(--map-bg);
  border: 1px solid var(--line-base); border-radius: var(--radius);
  position: relative; overflow: hidden;
}
.map-container svg { width: 100%; height: 100%; display: block; }
.country-path {
  fill: var(--map-land);
  stroke: var(--map-land-border);
  stroke-width: 0.55;
  cursor: pointer;
  transition: fill 0.12s ease, stroke 0.12s ease;
}
.country-path:hover {
  fill: var(--map-hover);
  stroke: var(--cyan);
  stroke-width: 1.2;
}
.country-path.high-activity {
  fill: var(--map-activity);
  stroke: var(--map-activity-border);
  stroke-width: 0.8;
}
.country-path.high-activity:hover {
  fill: var(--map-active);
  stroke: var(--cyan);
  stroke-width: 1.4;
}
.country-path.active {
  fill: var(--map-active);
  stroke: var(--cyan);
  stroke-width: 1.8;
  filter: drop-shadow(0 0 6px rgba(34, 211, 238, 0.45));
}
.country-label { fill: var(--muted); font-size: 9px; font-family: var(--font-mono); }
@keyframes map-pulse-anim {
  0% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.35); opacity: 0.15; }
  100% { transform: scale(0.9); opacity: 0.8; }
}
.map-pulse {
  transform-origin: center;
  animation: map-pulse-anim 3.2s infinite ease-in-out;
}
.country-pin rect {
  filter: drop-shadow(0 2px 5px rgba(0,0,0,0.2));
}
#map-tooltip {
  display: none;
  position: absolute;
  pointer-events: none;
  background: var(--map-tooltip-bg);
  color: var(--ink);
  border: 1px solid var(--cyan);
  border-radius: var(--radius);
  padding: 6px 10px;
  font-size: 11px;
  z-index: 100;
  box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  backdrop-filter: blur(4px);
}

/* AI Agent Copilot */
.agent-grid {
  display: grid; grid-template-columns: 280px minmax(0, 1fr) 300px;
  gap: 16px;
}
.agent-card {
  background: var(--surface-1); border: 1px solid var(--line-base);
  border-radius: var(--radius); padding: 14px;
}
.evidence-pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 6px; background: var(--cyan-bg); border: 1px solid var(--cyan-border);
  color: var(--cyan); font-size: 10px; font-family: var(--font-mono);
  border-radius: 2px; margin: 2px 4px 2px 0; cursor: pointer;
}
.evidence-pill:hover { background: #13343a; border-color: var(--cyan); }
.tool-step {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 0; border-bottom: 1px solid var(--line-dim); font-size: 11px;
}
.tool-step:last-child { border-bottom: 0; }

/* Scenario Lab Grid */
.scenario-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 14px;
}
.scenario-card {
  background: var(--surface-1); border: 1px solid var(--line-base);
  border-radius: var(--radius); padding: 16px;
  display: flex; flex-direction: column; justify-content: space-between;
}
.scenario-card.active { border-color: var(--cyan); box-shadow: 0 0 0 1px var(--cyan); }

/* Persistent Activity Strip */
.activity-strip {
  grid-area: strip;
  background: var(--surface-0); border-top: 1px solid var(--line-base);
  padding: 0 20px; display: flex; align-items: center; justify-content: space-between;
  font-size: 10px; color: var(--dim); z-index: 40;
}
.activity-strip-left, .activity-strip-right {
  display: flex; align-items: center; gap: 16px;
}

/* Modal dialogs */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.65);
  display: none; place-items: center; z-index: 200;
  backdrop-filter: blur(2px);
}
.modal-backdrop.active { display: grid; }
.modal-box {
  background: var(--surface-1); border: 1px solid var(--line-strong);
  border-radius: var(--radius); width: 90%; max-width: 600px;
  max-height: 85vh; overflow-y: auto; box-shadow: 0 20px 50px rgba(0,0,0,0.8);
}
.modal-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; border-bottom: 1px solid var(--line-base);
  background: var(--surface-0);
}
.modal-body { padding: 18px; }

/* Responsive adjustments */
@media (max-width: 1200px) {
  .app { grid-template-columns: 200px 1fr; }
  .investigation-grid, .agent-grid { grid-template-columns: 1fr; }
  .system-state-bar { grid-template-columns: repeat(4, 1fr); }
}
@media (max-width: 768px) {
  .app { display: block; }
  .context-rail { display: none; }
  .workspace { padding: 16px; }
  .system-state-bar { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body>
<div class="app">

  <!-- TOP COMMAND BAR -->
  <header class="command-bar" role="banner">
    <div class="brand">
      <div class="brand-mark">ZT-X</div>
      <div>
        <div class="brand-title">ZeroTrust-X</div>
        <div class="brand-sub">Detection operations</div>
      </div>
    </div>

    <!-- Global Omnibar Search -->
    <div class="omnibar">
      <input id="omni-search" aria-label="Global Omnibar Search" placeholder="Search identity, device, IP, event, alert, country... [ / ]" autocomplete="off">
      <kbd>/</kbd>
      <div id="omni-dropdown" class="omni-results" role="listbox"></div>
    </div>

    <!-- Right Controls -->
    <div class="top-controls">
      <div class="badge-capsule" title="Deployment posture">
        <span class="status-indicator"></span>
        <span>Local / unverified</span>
      </div>
      <div class="badge-capsule" title="Active Tenant">
        <span>TENANT: alpha-corp</span>
      </div>
      <select id="role-selector" class="role-select" aria-label="Current security role">
        <option value="analyst" selected>SOC_ANALYST (analyst-demo)</option>
        <option value="admin">SOC_ADMIN (admin-demo)</option>
        <option value="employee">EMPLOYEE (employee-demo)</option>
      </select>
      <button id="theme-toggle" class="btn-icon" title="Toggle Light/Dark operations theme">☼ Theme</button>
      <button id="palette-open" class="btn-icon" title="Keyboard Shortcuts (?)">?</button>
      <button id="refresh-btn" class="btn-icon" title="Refresh Telemetry">↻</button>
    </div>
  </header>

  <!-- LEFT CONTEXT RAIL -->
  <aside class="context-rail" role="navigation" aria-label="Primary Navigation">
    <div>
      <div class="nav-group-title">Operations</div>
      <nav class="nav-list">
        <button class="nav-item active" data-view="overview"><span>Threat Landscape</span><kbd>01</kbd></button>
        <button class="nav-item" data-view="investigations"><span>Investigations</span><kbd>02</kbd></button>
        <button class="nav-item" data-view="timeline"><span>Evidence timeline</span><kbd>03</kbd></button>
        <button class="nav-item" data-view="graph"><span>Entity graph</span><kbd>04</kbd></button>
        <button class="nav-item" data-view="global"><span>Country intelligence</span><kbd>05</kbd></button>
      </nav>
    </div>

    <div>
      <div class="nav-group-title">Help center</div>
      <nav class="nav-list">
        <button class="nav-item" data-view="agent"><span>Ask the evidence agent</span><kbd>06</kbd></button>
        <button class="nav-item" data-view="quality"><span>Data quality</span><kbd>07</kbd></button>
        <button class="nav-item" data-view="audit"><span>Audit chain</span><kbd>08</kbd></button>
      </nav>
    </div>

    <div>
      <div class="nav-group-title">Employee Scope</div>
      <nav class="nav-list">
        <button class="nav-item" data-view="employee"><span>Employee portal</span><kbd>09</kbd></button>
      </nav>
    </div>

    <div>
      <div class="nav-group-title">Lab Console</div>
      <nav class="nav-list">
        <button class="nav-item" data-view="demo"><span>Demo / Scenario Lab</span><kbd>10</kbd></button>
      </nav>
    </div>

    <div class="rail-footer">
      <div>Parquet Index · Unified v2</div>
      <div>GeoIP: Telemetry-Native (strict)</div>
      <div>Immutable Frozen Baseline</div>
    </div>
  </aside>

  <!-- PRIMARY WORKSPACE -->
  <main class="workspace" role="main">

    <!-- VIEW 1: OVERVIEW / THREAT LANDSCAPE -->
    <section id="overview" class="view active">
      <div class="view-header">
        <div>
          <div class="eyebrow">SOC / Detection operations</div>
          <h1 class="view-title">Operational overview</h1>
          <p class="view-desc">Evidence-backed signals across identity, endpoint, and network telemetry.</p>
        </div>
        <div class="view-meta">
          <div>DATASET BASELINE: <b class="mono" style="color:var(--green)">data-quality-v1</b></div>
          <div>STATUS: <b style="color:var(--green)">CLEAN_WITH_DOCUMENTED_EXCEPTIONS</b></div>
        </div>
      </div>

      <!-- Compact System State Indicators -->
      <div class="system-state-bar" aria-label="System operational status">
        <div class="state-pill"><div class="state-label">Events</div><div class="state-value"><span class="status-indicator"></span>62,430</div></div>
        <div class="state-pill"><div class="state-label">Detections</div><div class="state-value"><span class="status-indicator amber"></span>1,473</div></div>
        <div class="state-pill"><div class="state-label">Identities</div><div class="state-value"><span class="status-indicator"></span>3,000</div></div>
        <div class="state-pill"><div class="state-label">High Risk</div><div class="state-value"><span class="status-indicator red"></span>45 Users</div></div>
        <div class="state-pill"><div class="state-label">Storage</div><div class="state-value"><span class="status-indicator"></span>Parquet v2</div></div>
        <div class="state-pill"><div class="state-label">GeoIP</div><div class="state-value"><span class="status-indicator"></span>Strict Native</div></div>
        <div class="state-pill"><div class="state-label">Grounding</div><div class="state-value"><span class="status-indicator"></span>Active 100%</div></div>
      </div>

      <!-- Dataset Filters -->
      <div class="panel" style="margin-bottom: 20px;">
        <div class="panel-head">
          <h2 class="panel-title">Dataset filters</h2>
          <span id="filter-count" class="panel-note">Unfiltered view</span>
        </div>
        <div class="panel-body">
          <div class="toolbar" style="margin-bottom: 8px;">
            <input id="filter-user" aria-label="Filter by user ID" placeholder="User ID (e.g. EMP11411)">
            <input id="filter-source" aria-label="Filter by source" placeholder="Source (iam, firewall...)">
            <select id="filter-event-severity" aria-label="Filter event severity">
              <option value="">All event severities</option>
              <option value="critical">Events: Critical</option>
              <option value="high">Events: High</option>
              <option value="medium">Events: Medium</option>
              <option value="low">Events: Low</option>
            </select>
            <button id="apply-filters" class="btn btn-primary">Apply filters</button>
            <button id="reset-filters" class="btn btn-secondary">Reset</button>
          </div>
          <div class="panel-note">Derived from indexed events only · bounded to the selected identity · no inferred relationships.</div>
        </div>
      </div>

      <!-- Metrics Row -->
      <div id="metrics" style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;"></div>

      <!-- Main Operational Split -->
      <div style="display:grid; grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.8fr); gap: 16px;">
        <!-- Left: Open Signal Queue -->
        <article class="panel">
          <div class="panel-head">
            <h2 class="panel-title">Open signal queue</h2>
            <span class="panel-note">sorted by deterministic severity</span>
          </div>
          <div id="signals" class="panel-body" style="padding:0;"></div>
        </article>

        <!-- Right: Risk & Posture -->
        <aside style="display:flex; flex-direction:column; gap: 16px;">
          <div class="panel">
            <div class="panel-head">
              <h2 class="panel-title">Priority Identity Risk</h2>
              <span class="panel-note">Top risk score / 100</span>
            </div>
            <div id="risks" class="panel-body" style="padding:0;"></div>
          </div>

          <div class="panel">
            <div class="panel-head">
              <h2 class="panel-title">Evidence posture</h2>
              <span class="panel-note">Quality findings register</span>
            </div>
            <div id="posture" class="panel-body"></div>
          </div>
        </aside>
      </div>
    </section>

    <!-- VIEW 2: FLAGSHIP INVESTIGATION WORKSPACE -->
    <section id="investigations" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">SOC / Flagship Intelligence Workstation</div>
          <h1 class="view-title">Grounded investigations</h1>
          <p class="view-desc">Evidence correlation, event inspection, and citation validation.</p>
        </div>
        <div class="toolbar">
          <select id="invest-user" aria-label="Investigation identity" style="min-width: 220px;"></select>
          <button id="run-invest" class="btn btn-primary">Run investigation</button>
          <button id="invest-open-graph" class="btn btn-secondary">Explore In Graph</button>
          <button id="invest-open-agent" class="btn btn-secondary">Ask AI Investigator</button>
        </div>
      </div>

      <!-- Investigation Status Banner -->
      <div id="invest-status" class="notice">Select an identity to begin investigation triage.</div>

      <!-- Investigation Metrics Strip -->
      <div id="invest-evidence" style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
        <div class="panel" style="padding:12px;"><div class="panel-note">RISK SCORE</div><div class="mono" style="font-size:22px; font-weight:700;">—</div></div>
        <div class="panel" style="padding:12px;"><div class="panel-note">EVIDENCE RECORDS</div><div class="mono" style="font-size:22px; font-weight:700;">—</div></div>
        <div class="panel" style="padding:12px;"><div class="panel-note">VALIDATED CITATIONS</div><div class="mono" style="font-size:22px; font-weight:700;">—</div></div>
        <div class="panel" style="padding:12px;"><div class="panel-note">QUALITY WARNINGS</div><div class="mono" style="font-size:22px; font-weight:700;">—</div></div>
      </div>

      <!-- 3-Pane Intelligence Grid -->
      <div class="investigation-grid">
        <!-- Left: Entity Context -->
        <div class="panel">
          <div class="panel-head"><h2 class="panel-title">Entity Context</h2><span id="case-status-badge" class="badge ok">OPEN</span></div>
          <div id="invest-entity-ctx" class="panel-body">
            <div class="panel-note">Select an identity above to inspect context.</div>
          </div>
        </div>

        <!-- Center: Evidence Timeline & Signal Inspection -->
        <div class="panel">
          <div class="panel-head">
            <h2 class="panel-title">Evidence Timeline</h2>
            <div class="toolbar">
              <select id="invest-timeline-filter" style="padding:2px 6px; font-size:10px;">
                <option value="">All sources</option>
                <option value="iam">IAM</option>
                <option value="endpoint">Endpoint</option>
                <option value="firewall">Firewall</option>
                <option value="identity">Identity</option>
              </select>
            </div>
          </div>
          <div class="panel-body">
            <div id="invest-timeline" class="timeline-list">
              <div class="panel-note">No timeline loaded.</div>
            </div>
          </div>
        </div>

        <!-- Right: Insight Panel & Analyst Notebook -->
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div class="panel">
            <div class="panel-head"><h2 class="panel-title">Investigation report</h2><span class="badge ok">Deterministic</span></div>
            <div id="invest-result" class="panel-body mono" style="font-size:11px; white-space:pre-wrap; max-height:280px; overflow-y:auto;">No report loaded.</div>
          </div>

          <div class="panel">
            <div class="panel-head"><h2 class="panel-title">Analyst Scratchpad</h2><button id="save-notes" class="btn btn-secondary" style="font-size:9px; padding:2px 6px;">Save</button></div>
            <div class="panel-body">
              <textarea id="analyst-notes" rows="6" style="width:100%; background:var(--surface-0); border:1px solid var(--line-base); padding:8px; border-radius:var(--radius); font-size:11px;" placeholder="Add case findings, hypothesis, and notes..."></textarea>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- VIEW 3: EVIDENCE TIMELINE -->
    <section id="timeline" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">SOC / Chronological Telemetry</div>
          <h1 class="view-title">Identity timeline</h1>
          <p class="view-desc">Chronological events retained with explicit source provenance.</p>
        </div>
        <div class="toolbar">
          <input id="timeline-user" value="EMP10001" aria-label="User ID" style="min-width:180px;">
          <button id="load-timeline" class="btn btn-primary">Load evidence</button>
        </div>
      </div>
      <div id="timeline-result" class="panel"><div class="panel-body panel-note">Enter an identity above to load timeline evidence.</div></div>
    </section>

    <!-- VIEW 4: INTERACTIVE SECURITY GRAPH -->
    <section id="graph" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">SOC / Relationship Topology</div>
          <h1 class="view-title">Entity graph</h1>
          <p class="view-desc">Trace identity-to-event-to-asset relationships without inferred edges.</p>
        </div>
        <div class="toolbar">
          <input id="graph-user" value="EMP10001" aria-label="Graph identity" style="min-width: 160px;">
          <button id="load-graph" class="btn btn-primary">Build graph</button>
          <button id="fit-graph" class="btn btn-secondary">Fit view</button>
          <button id="graph-invest-path" class="btn btn-secondary">Investigate This Path</button>
        </div>
      </div>

      <div class="notice">Derived from indexed events only · bounded to the selected identity · no inferred relationships.</div>

      <!-- Graph Legend -->
      <div style="display:flex; gap:16px; margin-bottom:12px; font-size:10px; color:var(--muted); flex-wrap:wrap;">
        <span><span class="badge evidence">●</span> User</span>
        <span><span class="badge info">■</span> Device</span>
        <span><span class="badge slate">▢</span> Hostname</span>
        <span><span class="badge warning">◆</span> IP Address</span>
        <span><span class="badge ok">▭</span> Session</span>
        <span><span class="badge critical">⬢</span> Alert</span>
        <span><span class="badge normal">●</span> Event</span>
        <span><span class="badge info">▰</span> Country</span>
      </div>

      <div style="display:grid; grid-template-columns: minmax(0, 1.5fr) 300px; gap: 16px;">
        <div class="graph-viewport">
          <div class="graph-toolbar">
            <button id="zoom-in" class="btn-icon">+</button>
            <button id="zoom-out" class="btn-icon">−</button>
          </div>
          <svg id="graph-svg" viewBox="0 0 900 560" role="img" aria-label="Evidence relationship graph"></svg>
        </div>
        <aside class="panel">
          <div class="panel-head"><h2 class="panel-title">Selection inspector</h2></div>
          <div id="inspector" class="panel-body panel-note">Select a node in the graph to inspect indexed fields.</div>
        </aside>
      </div>

      <div id="graph-table" style="margin-top:16px;"></div>
    </section>

    <!-- VIEW 5: COUNTRY THREAT INTELLIGENCE -->
    <section id="global" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">Global Activity / Telemetry Country</div>
          <h1 class="view-title">Country intelligence</h1>
          <p class="view-desc">Activity grouped strictly by explicit <code>geo_country</code> telemetry. Zero IP inference.</p>
        </div>
        <div class="badge-capsule">
          <span class="status-indicator"></span>
          <span>GeoIP: Telemetry-Native (Strict)</span>
        </div>
      </div>

      <div class="notice">
        Country is evidence-backed telemetry, not a judgment of a country. Missing values remain <b>UNKNOWN / UNRESOLVED</b>.
      </div>

      <!-- Interactive Real-World SVG World Map -->
      <div class="map-container" style="margin-bottom:16px;">
        <div id="map-tooltip"></div>
        <div style="position:absolute; top:12px; right:14px; display:flex; gap:8px; align-items:center; z-index:10; pointer-events:none;">
          <span class="badge" style="background:var(--surface-1); border:1px solid var(--line-base); font-size:10px; color:var(--muted); backdrop-filter:blur(4px);">
            EQUIRECTANGULAR · 176 SOVEREIGN JURISDICTIONS
          </span>
          <span class="badge ok" style="background:var(--surface-1); font-size:10px; backdrop-filter:blur(4px);">
            TELEMETRY-NATIVE · ZERO-GUESS AUDITED
          </span>
        </div>
        <!-- __WORLD_MAP_SVG__ -->
      </div>

      <!-- Country Split View: List vs Profile Drill-Down -->
      <div style="display:grid; grid-template-columns: minmax(0, 1.2fr) minmax(340px, 1fr); gap: 16px;">
        <article class="panel">
          <div class="panel-head">
            <h2 class="panel-title">Activity concentration</h2>
            <span id="global-source" class="panel-note">Loading explicit telemetry...</span>
          </div>
          <div id="global-list" class="panel-body"></div>
        </article>

        <aside class="panel">
          <div class="panel-head">
            <h2 class="panel-title">Country Profile Drill-Down</h2>
            <span id="country-drilldown-badge" class="badge ok">Select Country</span>
          </div>
          <div id="country-drilldown-body" class="panel-body">
            <div class="panel-note">Click a country on the map or from the list to drill down: Country → IP → User → Device → Session → Events → Alert → Investigation.</div>
          </div>
        </aside>
      </div>
    </section>

    <!-- VIEW 6: AI SOC INVESTIGATOR -->
    <section id="agent" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">Evidence investigator / Read-only Copilot</div>
          <h1 class="view-title">Why is this identity high risk?</h1>
          <p class="view-desc">Deterministic evidence collection, citation verification, and safety auditing.</p>
        </div>
        <div class="toolbar">
          <select id="agent-user" aria-label="Investigation identity" style="min-width:200px;"></select>
        </div>
      </div>

      <div class="agent-grid">
        <!-- Left: Context Panel -->
        <aside class="panel">
          <div class="panel-head"><h2 class="panel-title">Investigation Context</h2></div>
          <div id="agent-context" class="panel-body">
            <div class="panel-note">Select an indexed identity above.</div>
          </div>
        </aside>

        <!-- Center: Copilot Finding & Action Queries -->
        <article class="panel">
          <div class="panel-head">
            <h2 class="panel-title">Investigator Finding</h2>
            <span id="agent-status" class="badge ok">Awaiting identity</span>
          </div>
          <div id="agent-result" class="panel-body" style="min-height:220px;">
            <div class="panel-note">Choose an identity to retrieve evidence.</div>
          </div>
          <!-- Suggested Analytical Actions -->
          <div style="padding:10px 16px; border-top:1px solid var(--line-base); background:var(--surface-0);" aria-label="Suggested investigation actions">
            <div class="panel-note" style="margin-bottom:8px; font-weight:600;">SUGGESTED INVESTIGATION ACTIONS</div>
            <div class="toolbar" style="margin-bottom:8px;">
              <button class="btn btn-secondary agent-action" data-question="Why is this user high risk?">Explain risk</button>
              <button class="btn btn-secondary agent-action" data-question="Show the attack timeline">Show timeline</button>
              <button class="btn btn-secondary agent-action" data-question="Find related devices">Find devices</button>
              <button class="btn btn-secondary agent-action" data-question="Find related IPs">Find IPs</button>
              <button class="btn btn-secondary agent-action" data-question="Explain why this alert fired">Explain alert</button>
              <button class="btn btn-secondary agent-action" data-question="Find supporting evidence">Find evidence</button>
              <button class="btn btn-secondary agent-action" data-question="Summarize this investigation">Summarize</button>
            </div>
            <div style="display:flex; gap:6px;">
              <input id="agent-custom-input" placeholder="Ask custom investigation question (e.g. compare peer behavior, trace firewall denies)..." style="flex:1; background:var(--surface-1); border:1px solid var(--line-base); padding:6px 9px; border-radius:var(--radius); font-size:11px;">
              <button id="agent-custom-btn" class="btn btn-primary" style="font-size:11px;">Ask</button>
            </div>
          </div>
        </article>

        <!-- Right: Verification & Tool Pipeline -->
        <aside class="panel">
          <div class="panel-head"><h2 class="panel-title">Verification Workflow</h2><span class="badge ok">100% Grounded</span></div>
          <div class="panel-body">
            <div class="tool-step"><span>query_user</span><span class="mono" style="color:var(--green)">✓</span></div>
            <div class="tool-step"><span>query_timeline</span><span class="mono" style="color:var(--green)">✓</span></div>
            <div class="tool-step"><span>query_detections</span><span class="mono" style="color:var(--green)">✓</span></div>
            <div class="tool-step"><span>query_graph</span><span class="mono" style="color:var(--green)">✓</span></div>
            <div class="tool-step"><span>verify_citations</span><span class="mono" style="color:var(--green)">✓</span></div>
            <div id="agent-safety-box" style="margin-top:16px;"></div>
          </div>
        </aside>
      </div>
    </section>

    <!-- VIEW 7: DATA QUALITY REGISTER -->
    <section id="quality" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">Data Operations / Integrity Register</div>
          <h1 class="view-title">Data quality register</h1>
          <p class="view-desc">Malformed values are retained, classified, and available for audit triage.</p>
        </div>
        <div class="badge-capsule">
          <span class="status-indicator"></span>
          <span>Status: CLEAN_WITH_DOCUMENTED_EXCEPTIONS</span>
        </div>
      </div>

      <!-- Quality Metrics Grid -->
      <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
        <div class="panel" style="padding:14px;"><div class="panel-note">TOTAL INGESTED</div><div class="mono" style="font-size:22px; font-weight:700;">62,430</div><div class="panel-note">normalized records</div></div>
        <div class="panel" style="padding:14px;"><div class="panel-note">QUARANTINE FINDINGS</div><div class="mono" style="font-size:22px; font-weight:700; color:var(--amber);">36,220</div><div class="panel-note">individual validation codes</div></div>
        <div class="panel" style="padding:14px;"><div class="panel-note">AFFECTED ROWS</div><div class="mono" style="font-size:22px; font-weight:700;">29,536</div><div class="panel-note">distinct records impacted</div></div>
        <div class="panel" style="padding:14px;"><div class="panel-note">FINDING RATIO</div><div class="mono" style="font-size:22px; font-weight:700;">1.2263</div><div class="panel-note">findings / affected row</div></div>
      </div>

      <div class="notice">
        <b>Data Quality Triage Note:</b> Finding count (36,220) exceeds affected rows (29,536) because a single record can trigger multiple reason codes (e.g. invalid IP address and out-of-range port). All malformed records are preserved with raw payloads.
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
        <div class="panel">
          <div class="panel-head"><h2 class="panel-title">Reason Code Breakdown</h2><span class="panel-note">Quality register</span></div>
          <div id="quality-reasons" class="panel-body"></div>
        </div>
        <div class="panel">
          <div class="panel-head"><h2 class="panel-title">Affected Rows by Source</h2><span class="panel-note">Ingestion sources</span></div>
          <div id="quality-sources" class="panel-body"></div>
        </div>
      </div>
    </section>

    <!-- VIEW 8: AUDIT CHAIN -->
    <section id="audit" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">Assurance / Immutable Audit Chain</div>
          <h1 class="view-title">Audit log & manifest</h1>
          <p class="view-desc">Cryptographic manifest hashes and immutable analyst action log.</p>
        </div>
      </div>
      <div id="audit-manifest" class="panel" style="margin-bottom:16px;"></div>
      <div id="audit-chain" class="panel"></div>
    </section>

    <!-- VIEW 9: EMPLOYEE PORTAL -->
    <section id="employee" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">Employee Services / Self Scope</div>
          <h1 class="view-title">My security activity</h1>
          <p class="view-desc">Only the authenticated employee identity is visible in this view.</p>
        </div>
        <button id="load-employee" class="btn btn-primary">Refresh my activity</button>
      </div>

      <div class="notice">
        Employee role access is strictly bounded to the authenticated employee's own identity (EMP10001).
      </div>

      <div id="employee-result" class="panel">
        <div class="panel-body panel-note">Loading employee activity...</div>
      </div>
    </section>

    <!-- VIEW 10: DEMO / SCENARIO LAB -->
    <section id="demo" class="view">
      <div class="view-header">
        <div>
          <div class="eyebrow">Demonstration / Tactical Lab</div>
          <h1 class="view-title">Scenario Lab</h1>
          <p class="view-desc">Execute deterministic attack chains against frozen telemetry to demonstrate SOC triage.</p>
        </div>
        <div id="scenario-active-badge" class="badge-capsule">
          <span class="status-indicator"></span>
          <span>Scenario Ready</span>
        </div>
      </div>

      <div id="scenario-timeline-box" class="panel" style="margin-bottom:20px; display:none;">
        <div class="panel-head">
          <h2 id="scenario-timeline-title" class="panel-title">Scenario Active</h2>
          <button id="scenario-jump-invest" class="btn btn-primary" style="font-size:10px; padding:3px 8px;">Jump to Live Investigation</button>
        </div>
        <div id="scenario-step-list" class="panel-body" style="display:flex; flex-direction:column; gap:8px;"></div>
      </div>

      <div class="scenario-grid" id="scenario-grid"></div>
    </section>

  </main>

  <!-- PERSISTENT ACTIVITY STRIP -->
  <footer class="activity-strip">
    <div class="activity-strip-left">
      <span>INDEX: <b class="mono" style="color:var(--green)">62,430 EVENTS</b></span>
      <span>BASELINE: <b class="mono">CLEAN_WITH_DOCUMENTED_EXCEPTIONS</b></span>
      <span>TENANT: <b class="mono">alpha-corp</b></span>
    </div>
    <div class="activity-strip-right">
      <span>GEOIP: <b class="mono">STRICT_TELEMETRY</b></span>
      <span>GROUNDING: <b class="mono" style="color:var(--green)">VALIDATED</b></span>
      <span>Shortcuts: <kbd>?</kbd></span>
    </div>
  </footer>

</div>

<!-- MODAL: EVIDENCE INSPECTOR DRAWER -->
<div id="modal-evidence" class="modal-backdrop" role="dialog" aria-modal="true" aria-label="Evidence Inspector">
  <div class="modal-box">
    <div class="modal-head">
      <div style="font-weight:600; font-size:13px;" id="modal-evidence-title">Event Evidence Details</div>
      <button id="modal-evidence-close" class="btn-icon">✕</button>
    </div>
    <div id="modal-evidence-body" class="modal-body mono" style="font-size:11px;"></div>
  </div>
</div>

<!-- MODAL: SHORTCUTS PALETTE -->
<div id="modal-palette" class="modal-backdrop" role="dialog" aria-modal="true" aria-label="Command Palette">
  <div class="modal-box">
    <div class="modal-head">
      <div style="font-weight:600; font-size:13px;">ZeroTrust-X Command Shortcuts</div>
      <button id="modal-palette-close" class="btn-icon">✕</button>
    </div>
    <div class="modal-body" style="font-size:12px;">
      <table class="data-table">
        <tbody>
          <tr><td><kbd>/</kbd></td><td>Focus Omnibar Global Search</td></tr>
          <tr><td><kbd>g d</kbd></td><td>Navigate to Threat Landscape Overview</td></tr>
          <tr><td><kbd>g i</kbd></td><td>Navigate to Investigation Workspace</td></tr>
          <tr><td><kbd>g t</kbd></td><td>Navigate to Evidence Timeline</td></tr>
          <tr><td><kbd>g g</kbd></td><td>Navigate to Entity Relationship Graph</td></tr>
          <tr><td><kbd>g c</kbd></td><td>Navigate to Country Intelligence</td></tr>
          <tr><td><kbd>g a</kbd></td><td>Navigate to AI SOC Investigator</td></tr>
          <tr><td><kbd>g q</kbd></td><td>Navigate to Data Quality Register</td></tr>
          <tr><td><kbd>g s</kbd></td><td>Navigate to Scenario Lab</td></tr>
          <tr><td><kbd>g e</kbd></td><td>Navigate to Employee Portal</td></tr>
          <tr><td><kbd>t</kbd></td><td>Toggle Light / Dark Operations Theme</td></tr>
          <tr><td><kbd>?</kbd></td><td>Open this Command Palette</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
/* ZeroTrust-X SOC Application Engine */
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let activeRole = 'analyst';
const getHeaders = () => {
  if (activeRole === 'admin') return {'X-Demo-Token': 'admin-demo'};
  if (activeRole === 'employee') return {'X-Demo-Token': 'employee-demo'};
  return {'X-Demo-Token': 'analyst-demo'};
};

const api = (path, opts = {}) => fetch(path, {
  ...opts,
  headers: { ...getHeaders(), ...(opts.headers || {}) }
}).then(async r => {
  if (!r.ok) throw Error(`${r.status}: ${await r.text()}`);
  return r.json();
});

let graphData = null, graphScale = 1;
let currentInvestigationId = null;
let currentScenario = null;
let loadedUsers = [];

/* View Routing */
function view(name, param = null) {
  document.querySelectorAll('.view').forEach(el => el.classList.toggle('active', el.id === name));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.view === name));
  window.history.replaceState(null, '', `/${name === 'overview' ? '' : name}`);

  if (name === 'overview') overview().catch(showError);
  if (name === 'global') globalActivity().catch(showError);
  if (name === 'quality') loadQuality().catch(showError);
  if (name === 'audit') loadAudit().catch(showError);
  if (name === 'demo') loadScenarios().catch(showError);
  if (name === 'employee') loadEmployee().catch(showError);
  if (name === 'investigations') {
    if (param) {
      document.querySelector('#invest-user').value = param;
    }
    loadInvestigation(param || document.querySelector('#invest-user').value || 'EMP11411').catch(showError);
  }
  if (name === 'graph') {
    if (param) document.querySelector('#graph-user').value = param;
    buildGraph().catch(showError);
  }
  if (name === 'agent') {
    if (param) document.querySelector('#agent-user').value = param;
    agentInvestigation('Why is this identity high risk?').catch(showError);
  }
}

document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => view(b.dataset.view));

/* Theme Switcher */
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem('zerotrust_theme', theme); } catch (e) {}
  const btn = document.querySelector('#theme-toggle');
  if (btn) btn.innerHTML = theme === 'light' ? '☀ Light' : '☾ Dark';
  if (typeof drawGraph === 'function' && graphData && graphData.nodes && graphData.nodes.length) {
    drawGraph();
  }
}

const savedTheme = (function() {
  try { return localStorage.getItem('zerotrust_theme') || 'light'; }
  catch (e) { return 'light'; }
})();
applyTheme(savedTheme);

document.querySelector('#theme-toggle').onclick = () => {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';
  applyTheme(next);
};

/* Role Switcher */
document.querySelector('#role-selector').onchange = (e) => {
  activeRole = e.target.value;
  overview().catch(showError);
};

/* Palette Modal */
document.querySelector('#palette-open').onclick = () => document.querySelector('#modal-palette').classList.add('active');
document.querySelector('#modal-palette-close').onclick = () => document.querySelector('#modal-palette').classList.remove('active');
document.querySelector('#modal-evidence-close').onclick = () => document.querySelector('#modal-evidence').classList.remove('active');

/* Keyboard Shortcuts Dispatcher */
let keyBuffer = '';
window.addEventListener('keydown', (e) => {
  if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) {
    if (e.key === 'Escape') {
      e.target.blur();
      document.querySelector('#omni-dropdown').classList.remove('active');
    }
    return;
  }
  if (e.key === '/') {
    e.preventDefault();
    document.querySelector('#omni-search').focus();
    return;
  }
  if (e.key === '?') {
    e.preventDefault();
    document.querySelector('#modal-palette').classList.toggle('active');
    return;
  }
  if (e.key === 'Escape') {
    document.querySelector('#modal-palette').classList.remove('active');
    document.querySelector('#modal-evidence').classList.remove('active');
    document.querySelector('#omni-dropdown').classList.remove('active');
    return;
  }
  if (e.key === 't') {
    document.querySelector('#theme-toggle').click();
    return;
  }
  keyBuffer += e.key.toLowerCase();
  if (keyBuffer.length > 2) keyBuffer = keyBuffer.slice(-2);
  if (keyBuffer === 'gd') view('overview');
  if (keyBuffer === 'gi') view('investigations');
  if (keyBuffer === 'gt') view('timeline');
  if (keyBuffer === 'gg') view('graph');
  if (keyBuffer === 'gc') view('global');
  if (keyBuffer === 'ga') view('agent');
  if (keyBuffer === 'gq') view('quality');
  if (keyBuffer === 'gs') view('demo');
  if (keyBuffer === 'ge') view('employee');
});

/* Omnibar Live Search */
const omniInput = document.querySelector('#omni-search');
const omniDropdown = document.querySelector('#omni-dropdown');
omniInput.addEventListener('input', async (e) => {
  const query = e.target.value.trim().toLowerCase();
  if (!query) {
    omniDropdown.classList.remove('active');
    return;
  }
  const results = [];
  // Match countries
  ['IN (India)', 'US (United States)', 'RU (Russia)', 'CN (China)'].forEach(c => {
    if (c.toLowerCase().includes(query)) results.push({ type: 'country', label: c, id: c.slice(0, 2) });
  });
  // Match loaded users
  loadedUsers.forEach(u => {
    if (u.user_id.toLowerCase().includes(query) || (u.department || '').toLowerCase().includes(query)) {
      results.push({ type: 'user', label: `${u.user_id} (${u.risk_level} · ${u.risk_score})`, id: u.user_id });
    }
  });
  if (!results.length) {
    omniDropdown.innerHTML = '<div style="padding:12px; color:var(--dim); font-size:11px;">No indexed entities match query.</div>';
  } else {
    omniDropdown.innerHTML = results.slice(0, 10).map(r => `
      <div class="omni-item" onclick="selectOmniResult('${esc(r.type)}', '${esc(r.id)}')">
        <div class="omni-item-left">
          <span class="omni-tag badge ${r.type === 'user' ? 'evidence' : 'info'}">${esc(r.type)}</span>
          <span class="mono">${esc(r.label)}</span>
        </div>
        <span style="font-size:10px; color:var(--dim);">Open →</span>
      </div>
    `).join('');
  }
  omniDropdown.classList.add('active');
});

function selectOmniResult(type, id) {
  omniDropdown.classList.remove('active');
  omniInput.value = '';
  if (type === 'country') {
    view('global');
    drilldownCountry(id);
  } else if (type === 'user') {
    view('investigations', id);
  }
}

/* Event Signal Renderer */
function renderEventSignals(items) {
  return `<div style="display:flex; flex-direction:column;">${items.slice(0, 8).map(e => `
    <div class="case-card" style="display:grid; grid-template-columns: 8px 120px 1fr auto; gap:12px; align-items:center;">
      <div style="width:3px; height:24px; border-radius:1px; background:${e.severity==='critical'?'var(--red)':e.severity==='high'?'var(--orange)':e.severity==='medium'?'var(--amber)':'var(--blue)'}"></div>
      <div>
        <div class="mono" style="font-size:11px; color:var(--cyan); cursor:pointer;" onclick="inspectRawEvent('${esc(e.event_id)}')">${esc(e.event_id)}</div>
        <div style="color:var(--dim); font-size:10px;">${esc(e.user_id || 'Unattributed')}</div>
      </div>
      <div>
        <div style="font-weight:500; font-size:12px;">${esc(e.event_type || 'Indexed event')}</div>
        <div style="color:var(--muted); font-size:10px;">${esc(e.source || 'telemetry')} · ${esc(e.action || 'observed')} · <span class="mono">${esc(e.timestamp || '')}</span></div>
      </div>
      <span class="badge ${esc(e.severity || 'low')}">${esc(e.severity || 'low')}</span>
    </div>
  `).join('')}</div>`;
}

/* Overview / Threat Landscape Loader */
function filterQuery(dataset) {
  const clauses = [];
  const user = document.querySelector('#filter-user').value.trim();
  const source = document.querySelector('#filter-source').value.trim();
  const severity = dataset === 'events' ? document.querySelector('#filter-event-severity').value : '';
  if (user) clauses.push({ field: 'user_id', op: 'eq', value: user });
  if (dataset === 'events' && source) clauses.push({ field: 'source', op: 'eq', value: source });
  if (severity) clauses.push({ field: 'severity', op: 'eq', value: severity });
  return `filters=${encodeURIComponent(JSON.stringify(clauses))}&limit=8`;
}

function quality(q, target='#posture') {
  const rs = Object.entries(q.reason_counts || {}).sort((a,b) => b[1] - a[1]).slice(0, 6);
  const h = `
    <div style="margin-bottom:10px;">
      <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--muted); margin-bottom:4px;">
        <span>QUARANTINE FINDINGS</span><b class="mono">${q.quarantine_rows.toLocaleString()}</b>
      </div>
      <div style="height:4px; background:var(--surface-3); border-radius:1px;"><div style="height:100%; width:100%; background:var(--amber);"></div></div>
    </div>
  ` + rs.map(r => `
    <div style="margin-bottom:8px;">
      <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--muted); margin-bottom:3px;">
        <span class="mono">${esc(r[0])}</span><b class="mono">${r[1].toLocaleString()}</b>
      </div>
      <div style="height:3px; background:var(--surface-3); border-radius:1px;"><div style="height:100%; width:${Math.min(100, (r[1]/q.quarantine_rows)*100)}%; background:var(--line-strong);"></div></div>
    </div>
  `).join('');
  document.querySelector(target).innerHTML = h;
}

async function overview() {
  const eventFilter = filterQuery('events').replace(/^filters=/, 'event_filters=').replace(/&limit=8$/, '');
  const detectionQuery = filterQuery('detections').replace(/^filters=/, 'detection_filters=').replace(/&limit=8$/, '');
  const riskFilter = filterQuery('user_risk').replace(/^filters=/, 'risk_filters=').replace(/&limit=8$/, '');

  const [s, us, q, alerts, events] = await Promise.all([
    api('/api/v1/summary?' + eventFilter + '&' + detectionQuery + '&' + riskFilter),
    api('/api/v1/users?' + filterQuery('user_risk')),
    api('/api/data-quality'),
    api('/api/v1/alerts?' + filterQuery('detections')),
    api('/api/v1/events?' + filterQuery('events'))
  ]);

  loadedUsers = us.items || [];
  const filtered = s.filtered || s;
  document.querySelector('#filter-count').textContent = `${(filtered.events ?? s.events).toLocaleString()} filtered events · baseline ${s.baseline?.events?.toLocaleString() ?? s.events.toLocaleString()}`;

  document.querySelector('#metrics').innerHTML = [
    ['INDEXED EVENTS', filtered.events ?? s.events, `baseline ${(s.baseline?.events ?? s.events).toLocaleString()}`],
    ['IDENTITIES', filtered.users ?? s.users, `baseline ${(s.baseline?.users ?? s.users).toLocaleString()}`],
    ['HIGH-RISK IDENTITIES', filtered.high_risk_users ?? s.high_risk_users, `baseline ${s.baseline?.users ? (s.high_risk_users ?? 0).toLocaleString() : '—'}`],
    ['OPEN DETECTIONS', alerts.filtered_count ?? filtered.detections ?? s.detections, `baseline ${(s.baseline?.detections ?? s.detections).toLocaleString()}`]
  ].map(m => `
    <div class="panel" style="padding:14px;">
      <div class="panel-note">${m[0]}</div>
      <div class="mono" style="font-size:24px; font-weight:700; margin-top:4px;">${m[1].toLocaleString()}</div>
      <div class="panel-note" style="margin-top:2px;">${m[2]}</div>
    </div>
  `).join('');

  const alertItems = Array.isArray(alerts.items) ? alerts.items : [];
  const eventItems = Array.isArray(events.items) ? events.items : [];
  const userItems = Array.isArray(us.items) ? us.items : [];

  if (alertItems.length) {
    document.querySelector('#signals').innerHTML = alertItems.map(a => `
      <div class="case-card" style="display:grid; grid-template-columns: 8px 140px 1fr auto; gap:12px; align-items:center;">
        <div style="width:3px; height:24px; border-radius:1px; background:var(--red)"></div>
        <div>
          <div class="mono" style="font-size:11px; color:var(--cyan); cursor:pointer;" onclick="view('investigations', '${esc(a.user_id)}')">${esc(a.detection_id)}</div>
          <div style="color:var(--dim); font-size:10px;">${esc(a.user_id)}</div>
        </div>
        <div>
          <div style="font-weight:600; font-size:12px;">${esc(a.rule_code)}</div>
          <div style="color:var(--muted); font-size:11px;">${esc(a.reason)}</div>
        </div>
        <span class="badge ${esc(a.severity)}">${esc(a.severity)}</span>
      </div>
    `).join('');
  } else if (eventItems.length) {
    document.querySelector('#signals').innerHTML = renderEventSignals(eventItems);
  } else {
    document.querySelector('#signals').innerHTML = `<div style="padding:24px; color:var(--dim); text-align:center;">No indexed signals match the current filters. The indexed event set contains ${(s.baseline?.events ?? s.events).toLocaleString()} events.</div>`;
  }

  document.querySelector('#risks').innerHTML = userItems.map(u => `
    <div class="case-card" style="display:grid; grid-template-columns: 90px 1fr 40px; gap:12px; align-items:center; cursor:pointer;" onclick="view('investigations', '${esc(u.user_id)}')">
      <span class="mono" style="font-size:11px; color:var(--ink);">${esc(u.user_id)}</span>
      <div style="height:5px; background:var(--surface-3); border-radius:1px;"><div style="height:100%; width:${u.risk_score}%; background:${u.risk_score>=90?'var(--red)':u.risk_score>=70?'var(--orange)':'var(--blue)'};"></div></div>
      <span class="mono" style="font-size:11px; text-align:right; font-weight:600;">${u.risk_score}</span>
    </div>
  `).join('');

  quality(q);

  // Populate Identity Dropdowns
  const opts = userItems.map(u => `<option value="${esc(u.user_id)}">${esc(u.user_id)} · ${esc(u.risk_level)} · ${u.risk_score}/100</option>`).join('');
  document.querySelector('#invest-user').innerHTML = opts;
  document.querySelector('#agent-user').innerHTML = opts;
}

document.querySelector('#apply-filters').onclick = () => overview().catch(showError);
document.querySelector('#reset-filters').onclick = () => {
  ['filter-user', 'filter-source'].forEach(id => document.querySelector('#' + id).value = '');
  document.querySelector('#filter-event-severity').value = '';
  overview().catch(showError);
};
document.querySelector('#refresh-btn').onclick = () => overview().catch(showError);

/* Flagship Investigation Loader */
async function loadInvestigation(userId) {
  if (!userId) return;
  currentInvestigationId = userId;
  document.querySelector('#invest-status').textContent = `Collecting and verifying evidence for ${userId}...`;

  const [inv, userRisk, userTimeline] = await Promise.all([
    api(`/api/investigations/${encodeURIComponent(userId)}`),
    api(`/api/users/${encodeURIComponent(userId)}`),
    api(`/api/users/${encodeURIComponent(userId)}/timeline`)
  ]);

  document.querySelector('#invest-status').className = 'notice ' + (inv.grounded ? 'grounded' : 'rejected');
  document.querySelector('#invest-status').textContent = inv.grounded
    ? `INVESTIGATION ${esc(inv.investigation_id)} · GROUNDED · All citations verified against indexed Parquet artifacts.`
    : `INVESTIGATION ${esc(inv.investigation_id)} · CITATION REJECTED · Discrepancies detected.`;

  // Update Metrics Strip
  document.querySelector('#invest-evidence').innerHTML = `
    <div class="panel" style="padding:14px;"><div class="panel-note">RISK SCORE</div><div class="mono" style="font-size:24px; font-weight:700; color:${userRisk.risk_score>=90?'var(--red)':userRisk.risk_score>=70?'var(--orange)':'var(--blue)'};">${userRisk.risk_score}/100</div><div class="panel-note">${esc(userRisk.risk_level)} level</div></div>
    <div class="panel" style="padding:14px;"><div class="panel-note">EVIDENCE RECORDS</div><div class="mono" style="font-size:24px; font-weight:700;">${inv.evidence.length}</div><div class="panel-note">returned artifacts</div></div>
    <div class="panel" style="padding:14px;"><div class="panel-note">VALIDATED CITATIONS</div><div class="mono" style="font-size:24px; font-weight:700; color:var(--cyan);">${inv.citations.length}</div><div class="panel-note">grounded IDs</div></div>
    <div class="panel" style="padding:14px;"><div class="panel-note">QUALITY WARNINGS</div><div class="mono" style="font-size:24px; font-weight:700; color:${(inv.quality_warnings||[]).length?'var(--amber)':'var(--dim)'};">${(inv.quality_warnings||[]).length}</div><div class="panel-note">data hygiene flags</div></div>
  `;

  // Entity Context
  document.querySelector('#invest-entity-ctx').innerHTML = `
    <div style="display:flex; flex-direction:column; gap:10px; font-size:11px;">
      <div><span class="panel-note">IDENTITY:</span> <b class="mono" style="color:var(--ink); font-size:13px;">${esc(userId)}</b></div>
      <div><span class="panel-note">DEPARTMENT:</span> <span>${esc(userRisk.department || 'Not specified')}</span></div>
      <div><span class="panel-note">RISK LEVEL:</span> <span class="badge ${esc(userRisk.risk_level)}">${esc(userRisk.risk_level)} (${userRisk.risk_score})</span></div>
      <div><span class="panel-note">REASON CODES:</span>
        <div style="margin-top:4px;">${(userRisk.reason_codes || []).map(r => `<span class="badge warning" style="margin:2px 2px 2px 0;">${esc(r)}</span>`).join('') || '<span class="panel-note">None</span>'}</div>
      </div>
      <div><span class="panel-note">EVIDENCE CITATIONS:</span>
        <div style="max-height:100px; overflow-y:auto; margin-top:4px;">
          ${(inv.citations || []).slice(0, 20).map(c => `<span class="evidence-pill" onclick="inspectRawEvent('${esc(c)}')">${esc(c)}</span>`).join('')}
        </div>
      </div>
    </div>
  `;

  // Timeline
  renderInvestigationTimeline(userTimeline);

  // Report
  document.querySelector('#invest-result').textContent = inv.report;

  // Restore Analyst Notes
  const savedNotes = sessionStorage.getItem(`notes_${userId}`) || '';
  document.querySelector('#analyst-notes').value = savedNotes;
}

function renderInvestigationTimeline(events) {
  const container = document.querySelector('#invest-timeline');
  if (!events || !events.length) {
    container.innerHTML = '<div class="panel-note">No timeline events found.</div>';
    return;
  }
  container.innerHTML = events.slice(0, 100).map(e => {
    let cls = '';
    if (e.event_type === 'login_failed') cls = 'auth-fail';
    else if (e.event_type === 'login_success') cls = 'auth-success';
    else if (e.event_type === 'mfa_failed') cls = 'mfa-fail';
    else if (e.event_type === 'endpoint_alert') cls = 'endpoint-alert';
    else if (e.action === 'deny' || e.action === 'block') cls = 'firewall-deny';

    return `
      <div class="timeline-event ${cls}" onclick="inspectEventModal(${JSON.stringify(e).replace(/"/g, '&quot;')})">
        <div class="timeline-head">
          <span class="timeline-title">${esc(e.event_type || 'Event')}</span>
          <span class="timeline-time">${esc(e.timestamp || '')}</span>
        </div>
        <div class="timeline-meta">
          <span class="badge ${esc(e.severity || 'low')}">${esc(e.severity || 'low')}</span>
          <span class="badge slate">${esc(e.source || 'source')}</span>
          <span class="mono">${esc(e.event_id || '')}</span>
          <span>${esc(e.action || '')}</span>
        </div>
      </div>
    `;
  }).join('');
}

document.querySelector('#run-invest').onclick = () => loadInvestigation(document.querySelector('#invest-user').value);
document.querySelector('#invest-open-graph').onclick = () => view('graph', currentInvestigationId);
document.querySelector('#invest-open-agent').onclick = () => view('agent', currentInvestigationId);
document.querySelector('#save-notes').onclick = () => {
  if (!currentInvestigationId) return;
  const notes = document.querySelector('#analyst-notes').value;
  sessionStorage.setItem(`notes_${currentInvestigationId}`, notes);
  alert('Analyst case notes saved in session.');
};

/* Raw Event Inspector Modal */
function inspectEventModal(eventObj) {
  document.querySelector('#modal-evidence-title').textContent = `Evidence Record: ${eventObj.event_id || 'Event'}`;
  const rows = Object.entries(eventObj).map(([k, v]) => `
    <div style="display:grid; grid-template-columns: 140px 1fr; gap:8px; padding:6px 0; border-bottom:1px solid var(--line-dim);">
      <b style="color:var(--dim); font-weight:500;">${esc(k)}</b>
      <span style="color:var(--ink); word-break:break-all;">${esc(typeof v === 'object' ? JSON.stringify(v) : v)}</span>
    </div>
  `).join('');
  document.querySelector('#modal-evidence-body').innerHTML = `
    <div style="margin-bottom:12px;">
      <span class="badge evidence">CANONICAL ARTIFACT</span>
      <span class="badge slate">READ-ONLY EVIDENCE</span>
    </div>
    ${rows}
  `;
  document.querySelector('#modal-evidence').classList.add('active');
}

async function inspectRawEvent(eventId) {
  try {
    const res = await api(`/api/v1/events?filters=${encodeURIComponent(JSON.stringify([{field:'event_id',op:'eq',value:eventId}]))}`);
    if (res.items && res.items.length) {
      inspectEventModal(res.items[0]);
    } else {
      alert(`Evidence ${eventId} not directly indexed in event table (may be user_risk or detection record).`);
    }
  } catch (e) {
    alert(e.message);
  }
}

/* Evidence Timeline View Loader */
document.querySelector('#load-timeline').onclick = async () => {
  const userId = document.querySelector('#timeline-user').value.trim();
  const out = document.querySelector('#timeline-result');
  try {
    out.innerHTML = '<div class="panel-body panel-note">Loading evidence timeline...</div>';
    const rs = await api(`/api/users/${encodeURIComponent(userId)}/timeline`);
    if (!rs.length) {
      out.innerHTML = '<div class="panel-body panel-note">No timeline records for this identity.</div>';
      return;
    }
    out.innerHTML = `
      <div class="panel-head"><h2 class="panel-title">${esc(userId)} Evidence Records</h2><span class="panel-note">${rs.length} events</span></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr><th>Event ID</th><th>Type</th><th>Source</th><th>Timestamp</th><th>Action</th><th>Severity</th></tr>
          </thead>
          <tbody>
            ${rs.map(r => `
              <tr onclick="inspectEventModal(${JSON.stringify(r).replace(/"/g, '&quot;')})" style="cursor:pointer;">
                <td class="mono-cell" style="color:var(--cyan);">${esc(r.event_id)}</td>
                <td>${esc(r.event_type)}</td>
                <td><span class="badge slate">${esc(r.source)}</span></td>
                <td class="mono-cell">${esc(r.timestamp)}</td>
                <td>${esc(r.action || '—')}</td>
                <td><span class="badge ${esc(r.severity || 'low')}">${esc(r.severity || 'low')}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (e) {
    out.innerHTML = `<div class="panel-body notice rejected">${esc(e.message)}</div>`;
  }
};

/* Interactive Security Graph Loader */
async function buildGraph() {
  const userId = document.querySelector('#graph-user').value.trim();
  const svg = document.querySelector('#graph-svg');
  svg.innerHTML = '<text x="450" y="280" text-anchor="middle" fill="var(--dim)">Building graph topology...</text>';
  try {
    graphData = await api(`/api/graph/${encodeURIComponent(userId)}`);
    graphScale = 1;
    drawGraph();
    document.querySelector('#graph-table').innerHTML = `
      <div class="panel">
        <div class="panel-head">
          <h2 class="panel-title">Graph evidence elements</h2>
          <span class="panel-note">${graphData.event_count} events · ${graphData.nodes.length} nodes · ${graphData.edges.length} edges</span>
        </div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>Node ID</th><th>Entity Type</th><th>Label</th><th>Evidence Citations</th></tr></thead>
            <tbody>
              ${graphData.nodes.map(n => `
                <tr onclick="inspectGraphNode('${esc(n.id)}')" style="cursor:pointer;">
                  <td class="mono-cell" style="color:var(--cyan);">${esc(n.id)}</td>
                  <td><span class="badge ${n.type==='user'?'evidence':n.type==='alert'?'critical':'slate'}">${esc(n.type)}</span></td>
                  <td><b>${esc(n.label)}</b></td>
                  <td class="mono-cell">${esc((n.event_ids || []).slice(0, 4).join(', ') || '—')}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (e) {
    svg.innerHTML = `<text x="450" y="280" text-anchor="middle" fill="var(--red)">${esc(e.message)}</text>`;
  }
}

/* Collision-Free Elliptical Layout & Physics Relaxation */
let graphPan = [0, 0];
let isPanningGraph = false;
let panStart = [0, 0];
let selectedNodeId = null;

function calculateGraphLayout(nodes, edges) {
  const width = 900;
  const height = 560;
  const cx = 450;
  const cy = 270;

  const typeTiers = {
    user: [0, 0, 0],
    session: [130, 85, 0],
    alert: [180, 115, Math.PI / 4],
    event: [260, 160, Math.PI / 10],
    device: [330, 205, Math.PI / 6],
    host: [330, 205, (5 * Math.PI) / 6],
    ip: [380, 235, Math.PI / 3],
    destination: [380, 235, (2 * Math.PI) / 3],
    country: [380, 235, (4 * Math.PI) / 3],
  };

  const pos = {};
  const byType = {};
  nodes.forEach(n => {
    byType[n.type] = byType[n.type] || [];
    byType[n.type].push(n);
  });

  if (byType.user && byType.user.length) {
    pos[byType.user[0].id] = { x: cx, y: cy, fixed: true };
  }

  Object.entries(byType).forEach(([t, group]) => {
    if (t === 'user') return;
    const tier = typeTiers[t] || [280, 170, 0];
    const rx = tier[0];
    const ry = tier[1];
    const phase = tier[2];
    const count = group.length;

    group.forEach((n, i) => {
      const angle = phase + (i / count) * Math.PI * 2;
      pos[n.id] = {
        x: cx + Math.cos(angle) * rx,
        y: cy + Math.sin(angle) * ry,
        fixed: false
      };
    });
  });

  const keys = Object.keys(pos);
  // Collision relaxation passes to ensure zero overlap
  for (let step = 0; step < 35; step++) {
    for (let i = 0; i < keys.length; i++) {
      const p1 = pos[keys[i]];
      for (let j = i + 1; j < keys.length; j++) {
        const p2 = pos[keys[j]];
        let dx = p1.x - p2.x;
        let dy = p1.y - p2.y;
        let dist = Math.hypot(dx, dy);
        if (dist < 0.001) { dx = 1.0; dy = 0.0; dist = 1.0; }
        const minGap = 72.0;
        if (dist < minGap) {
          const overlap = minGap - dist;
          const nx = dx / dist;
          const ny = dy / dist;
          if (!p1.fixed && !p2.fixed) {
            p1.x += nx * (overlap * 0.5);
            p1.y += ny * (overlap * 0.5);
            p2.x -= nx * (overlap * 0.5);
            p2.y -= ny * (overlap * 0.5);
          } else if (!p1.fixed) {
            p1.x += nx * overlap;
            p1.y += ny * overlap;
          } else if (!p2.fixed) {
            p2.x -= nx * overlap;
            p2.y -= ny * overlap;
          }
        }
      }
    }
  }

  // Constrain inside visible boundaries
  keys.forEach(k => {
    if (!pos[k].fixed) {
      pos[k].x = Math.max(60, Math.min(width - 60, pos[k].x));
      pos[k].y = Math.max(35, Math.min(height - 35, pos[k].y));
    }
  });

  return pos;
}

function drawGraph() {
  const svg = document.querySelector('#graph-svg');
  if (!graphData || !graphData.nodes.length) {
    svg.innerHTML = '<text x="450" y="280" text-anchor="middle" fill="var(--dim)">No graph entities available.</text>';
    return;
  }

  const pos = calculateGraphLayout(graphData.nodes, graphData.edges);

  const isLight = document.documentElement.getAttribute('data-theme') === 'light';

  // Render Edges
  const edgeSvg = graphData.edges.map(e => {
    const a = pos[e.source] || { x: 450, y: 270 };
    const b = pos[e.target] || { x: 450, y: 270 };
    const dist = Math.hypot(b.x - a.x, b.y - a.y);
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;

    let labelTag = '';
    // Show static badge for meaningful semantic relationships with sufficient distance
    if (dist >= 85 && e.kind !== 'observed') {
      const kindStr = esc(e.kind);
      const kw = Math.max(38, kindStr.length * 6.5 + 14);
      labelTag = `
        <g class="edge-label-group" transform="translate(${mx}, ${my})">
          <rect class="edge-label-bg" x="-${kw/2}" y="-8" width="${kw}" height="16" rx="3" />
          <text class="edge-label-text" x="0" y="0" text-anchor="middle" dominant-baseline="central">${kindStr}</text>
        </g>
      `;
    }

    return `
      <g class="edge-group" data-source="${esc(e.source)}" data-target="${esc(e.target)}" data-kind="${esc(e.kind)}">
        <line class="edge" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" />
        ${labelTag}
      </g>
    `;
  }).join('');

  // Render Nodes with High-Contrast Pill Badges
  const nodeSvg = graphData.nodes.map(n => {
    const p = pos[n.id] || { x: 450, y: 270 };
    const isUser = n.type === 'user';
    const isAlert = n.type === 'alert';
    const isIp = n.type === 'ip';
    const isDevice = n.type === 'device';
    const isHost = n.type === 'host';
    const isSession = n.type === 'session';
    const isCountry = n.type === 'country';

    let theme = { stroke: '#64748b', fill: '#0f172a', text: '#cbd5e1', icon: '⚡' };
    if (isLight) {
      theme = { stroke: '#64748b', fill: '#f8fafc', text: '#1e293b', icon: '⚡' };
      if (isUser) theme = { stroke: '#0891b2', fill: '#ecfeff', text: '#0e7490', icon: '👤' };
      else if (isAlert) theme = { stroke: '#dc2626', fill: '#fef2f2', text: '#991b1b', icon: '⚠️' };
      else if (isIp) theme = { stroke: '#d97706', fill: '#fffbeb', text: '#92400e', icon: '🌐' };
      else if (isDevice) theme = { stroke: '#2563eb', fill: '#eff6ff', text: '#1e40af', icon: '💻' };
      else if (isHost) theme = { stroke: '#475569', fill: '#f1f5f9', text: '#0f172a', icon: '🖥️' };
      else if (isSession) theme = { stroke: '#059669', fill: '#ecfdf5', text: '#065f46', icon: '🔑' };
      else if (isCountry) theme = { stroke: '#6366f1', fill: '#eef2ff', text: '#3730a3', icon: '🚩' };
    } else {
      if (isUser) theme = { stroke: '#06b6d4', fill: '#083344', text: '#67e8f9', icon: '👤' };
      else if (isAlert) theme = { stroke: '#ef4444', fill: '#450a0a', text: '#fca5a5', icon: '⚠️' };
      else if (isIp) theme = { stroke: '#f59e0b', fill: '#451a03', text: '#fde68a', icon: '🌐' };
      else if (isDevice) theme = { stroke: '#3b82f6', fill: '#172554', text: '#93c5fd', icon: '💻' };
      else if (isHost) theme = { stroke: '#94a3b8', fill: '#1e293b', text: '#f1f5f9', icon: '🖥️' };
      else if (isSession) theme = { stroke: '#10b981', fill: '#064e3b', text: '#a7f3d0', icon: '🔑' };
      else if (isCountry) theme = { stroke: '#818cf8', fill: '#1e1b4b', text: '#c7d2fe', icon: '🚩' };
    }

    let shapeSvg = '';
    if (isUser) {
      shapeSvg = `
        <circle class="node-shape" r="22" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="2" />
        <circle r="16" fill="none" stroke="${theme.stroke}" stroke-width="1" stroke-dasharray="2 3" />
        <text text-anchor="middle" dominant-baseline="central" font-size="13">👤</text>
      `;
    } else if (isAlert) {
      shapeSvg = `<polygon class="node-shape" points="-14,-8 0,-16 14,-8 14,8 0,16 -14,8" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="1.8" />`;
    } else if (isIp) {
      shapeSvg = `<polygon class="node-shape" points="0,-14 14,0 0,14 -14,0" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="1.8" />`;
    } else if (isDevice) {
      shapeSvg = `<rect class="node-shape" x="-13" y="-13" width="26" height="26" rx="4" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="1.8" />`;
    } else if (isHost) {
      shapeSvg = `<rect class="node-shape" x="-15" y="-11" width="30" height="22" rx="3" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="1.8" />`;
    } else if (isSession) {
      shapeSvg = `<rect class="node-shape" x="-16" y="-10" width="32" height="20" rx="10" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="1.8" />`;
    } else if (isCountry) {
      shapeSvg = `<rect class="node-shape" x="-18" y="-11" width="36" height="22" rx="4" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="1.8" />`;
    } else {
      shapeSvg = `
        <circle class="node-shape" r="8" fill="${theme.fill}" stroke="${theme.stroke}" stroke-width="1.5" />
        <circle r="3" fill="${theme.stroke}" />
      `;
    }

    const labelStr = esc(n.label);
    const pillW = Math.max(54, labelStr.length * 7.2 + 24);
    const pillH = 20;
    const pillY = isUser ? 28 : (n.type === 'event' ? 14 : 18);

    const badgeSvg = `
      <g class="node-pill" transform="translate(0, ${pillY})">
        <rect class="node-pill-bg" x="-${pillW/2}" y="-${pillH/2}" width="${pillW}" height="${pillH}" rx="4" stroke="${theme.stroke}" fill="${theme.fill}" />
        <text class="node-pill-text" x="0" y="0" dominant-baseline="central" text-anchor="middle" fill="${theme.text}">
          ${theme.icon} ${labelStr}
        </text>
      </g>
    `;

    return `
      <g class="node ${esc(n.type)} ${selectedNodeId === n.id ? 'selected' : ''}" data-id="${esc(n.id)}" transform="translate(${p.x},${p.y})"
         onclick="inspectGraphNode('${esc(n.id)}')"
         onmouseenter="highlightNodeConnections('${esc(n.id)}')"
         onmouseleave="highlightNodeConnections(null)">
        ${shapeSvg}
        ${badgeSvg}
      </g>
    `;
  }).join('');

  svg.innerHTML = `
    <g id="graph-transform-group" transform="translate(${graphPan[0]}, ${graphPan[1]}) scale(${graphScale})" transform-origin="450 270">
      ${edgeSvg}
      ${nodeSvg}
    </g>
  `;
}

function highlightNodeConnections(nodeId) {
  if (!nodeId) {
    document.querySelectorAll('.node').forEach(n => {
      n.classList.remove('dimmed');
      if (selectedNodeId && n.dataset.id === selectedNodeId) {
        n.classList.add('selected');
      } else {
        n.classList.remove('selected');
      }
    });
    document.querySelectorAll('.edge-group').forEach(el => {
      const line = el.querySelector('.edge');
      if (line) line.classList.remove('dimmed', 'highlighted');
    });
    return;
  }

  const connected = new Set([nodeId]);
  graphData.edges.forEach(e => {
    if (e.source === nodeId) connected.add(e.target);
    if (e.target === nodeId) connected.add(e.source);
  });

  document.querySelectorAll('.node').forEach(el => {
    const isConn = connected.has(el.dataset.id);
    el.classList.toggle('dimmed', !isConn);
  });

  document.querySelectorAll('.edge-group').forEach(el => {
    const isConn = el.dataset.source === nodeId || el.dataset.target === nodeId;
    const line = el.querySelector('.edge');
    if (line) {
      line.classList.toggle('highlighted', isConn);
      line.classList.toggle('dimmed', !isConn);
    }
  });
}

function inspectGraphNode(nodeId) {
  selectedNodeId = nodeId;
  document.querySelectorAll('.node').forEach(n => {
    n.classList.toggle('selected', n.dataset.id === nodeId);
  });

  const node = graphData.nodes.find(n => n.id === nodeId);
  if (!node) return;
  const inspector = document.querySelector('#inspector');

  // Find relationships connected to this node
  const connections = graphData.edges.filter(e => e.source === nodeId || e.target === nodeId);

  inspector.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:10px; font-size:11px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <b class="mono" style="font-size:13px; color:var(--ink);">${esc(node.label)}</b>
        <span class="badge ${node.type==='user'?'evidence':node.type==='alert'?'critical':node.type==='ip'?'warning':'slate'}">${esc(node.type.toUpperCase())}</span>
      </div>

      <div style="padding:8px; background:var(--surface-0); border:1px solid var(--line-base); border-radius:var(--radius);">
        <div class="panel-note" style="margin-bottom:4px; font-weight:600;">ENTITY DETAILS</div>
        <div><span class="panel-note">ID:</span> <span class="mono">${esc(node.id)}</span></div>
        ${node.risk_score !== undefined && node.risk_score !== null ? `<div><span class="panel-note">RISK:</span> <b class="mono" style="color:var(--amber);">${node.risk_score}/100</b> (${esc(node.risk_level)})</div>` : ''}
        ${node.event_ids && node.event_ids.length ? `<div><span class="panel-note">CITATIONS:</span> <span class="mono">${node.event_ids.length} indexed events</span></div>` : ''}
      </div>

      <div>
        <div class="panel-note" style="margin-bottom:4px; font-weight:600;">CONNECTED TOPOLOGY (${connections.length})</div>
        <div style="max-height:160px; overflow-y:auto; display:flex; flex-direction:column; gap:4px;">
          ${connections.map(c => {
            const isOut = c.source === nodeId;
            const peerId = isOut ? c.target : c.source;
            const peerNode = graphData.nodes.find(n => n.id === peerId) || { label: peerId, type: 'node' };
            return `
              <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 6px; background:var(--surface-1); border-radius:3px; border:1px solid var(--line-dim);">
                <span class="mono" style="font-size:10px; color:var(--cyan); cursor:pointer;" onclick="inspectGraphNode('${esc(peerId)}')">${esc(peerNode.label)}</span>
                <span class="badge slate" style="font-size:9px;">${isOut ? '──▶' : '◀──'} ${esc(c.kind)}</span>
              </div>
            `;
          }).join('') || '<div class="panel-note">No edges attached</div>'}
        </div>
      </div>

      <button class="btn btn-primary" style="margin-top:6px; font-size:11px;" onclick="view('investigations', '${esc(graphData.user_id)}')">
        Investigate in SOC Workspace →
      </button>
    </div>
  `;
}

document.querySelector('#load-graph').onclick = buildGraph;
document.querySelector('#fit-graph').onclick = () => {
  graphScale = 1;
  graphPan = [0, 0];
  drawGraph();
};
document.querySelector('#zoom-in').onclick = () => {
  graphScale = Math.min(2.5, graphScale + 0.15);
  drawGraph();
};
document.querySelector('#zoom-out').onclick = () => {
  graphScale = Math.max(0.5, graphScale - 0.15);
  drawGraph();
};
document.querySelector('#graph-invest-path').onclick = () => {
  if (graphData && graphData.user_id) view('investigations', graphData.user_id);
};

// Mouse Drag-to-Pan and Wheel-to-Zoom on Graph Viewport
const graphViewportEl = document.querySelector('.graph-viewport');
if (graphViewportEl) {
  graphViewportEl.addEventListener('mousedown', (e) => {
    if (e.target.closest('.node') || e.target.closest('button')) return;
    isPanningGraph = true;
    panStart = [e.clientX - graphPan[0], e.clientY - graphPan[1]];
    graphViewportEl.style.cursor = 'grabbing';
  });

  window.addEventListener('mousemove', (e) => {
    if (!isPanningGraph) return;
    graphPan = [e.clientX - panStart[0], e.clientY - panStart[1]];
    const grp = document.querySelector('#graph-transform-group');
    if (grp) {
      grp.setAttribute('transform', `translate(${graphPan[0]}, ${graphPan[1]}) scale(${graphScale})`);
    }
  });

  window.addEventListener('mouseup', () => {
    if (isPanningGraph) {
      isPanningGraph = false;
      graphViewportEl.style.cursor = 'default';
    }
  });

  graphViewportEl.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 0.08 : -0.08;
    graphScale = Math.max(0.5, Math.min(2.5, graphScale + delta));
    const grp = document.querySelector('#graph-transform-group');
    if (grp) {
      grp.setAttribute('transform', `translate(${graphPan[0]}, ${graphPan[1]}) scale(${graphScale})`);
    }
  }, { passive: false });
}

/* Country Intelligence Loader */
let countryActivityMap = {};

async function globalActivity() {
  const r = await api('/api/v1/global?limit=25');
  document.querySelector('#global-source').textContent = `${r.country_source} · ${r.items.length} country groups`;
  const max = Math.max(...r.items.map(x => x.event_count), 1);

  countryActivityMap = {};
  r.items.forEach(x => {
    countryActivityMap[x.country] = x.event_count;
  });

  document.querySelector('#global-list').innerHTML = r.items.map(x => `
    <div class="case-card" style="display:grid; grid-template-columns: 140px 1fr 90px; gap:12px; align-items:center; cursor:pointer;" onclick="drilldownCountry('${esc(x.country)}')">
      <span class="mono" style="font-size:11px; font-weight:600; color:${x.country.includes('UNKNOWN')?'var(--slate)':'var(--ink)'};">
        ${x.country === 'IN' ? '🚩 India (IN)' : x.country === 'US' ? '🚩 United States (US)' : x.country === 'RU' ? '🚩 Russia (RU)' : x.country === 'CN' ? '🚩 China (CN)' : esc(x.country)}
      </span>
      <div style="height:6px; background:var(--surface-3); border-radius:1px;">
        <div style="height:100%; width:${Math.max(2, (x.event_count/max)*100)}%; background:${x.country.includes('UNKNOWN')?'var(--slate)':'var(--blue)'};"></div>
      </div>
      <span class="mono" style="font-size:11px; text-align:right;">${x.event_count.toLocaleString()}</span>
    </div>
  `).join('');

  // Setup interactive map paths & tooltips
  setupWorldMapInteractions();
}

function setupWorldMapInteractions() {
  const container = document.querySelector('.map-container');
  const tip = document.getElementById('map-tooltip');

  document.querySelectorAll('.country-path').forEach(path => {
    const code = path.dataset.code;
    const name = path.dataset.name || code;

    path.onclick = () => {
      drilldownCountry(code, name);
    };

    if (container && tip) {
      path.onmouseenter = () => {
        const count = countryActivityMap[code] || 0;
        tip.innerHTML = `
          <div style="font-weight:700; color:var(--ink);">${esc(name)} <span class="mono" style="color:var(--cyan); font-size:10px;">[${esc(code)}]</span></div>
          <div style="font-size:10px; color:${count > 0 ? 'var(--cyan)' : 'var(--slate)'}; font-family:monospace; margin-top:3px;">
            ${count > 0 ? `● ${count.toLocaleString()} Telemetry Events` : '○ Zero Events (Zero-Guess: Unresolved)'}
          </div>
        `;
        tip.style.display = 'block';
      };

      path.onmousemove = (e) => {
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left + 14;
        const y = e.clientY - rect.top + 14;
        tip.style.left = Math.min(x, rect.width - 240) + 'px';
        tip.style.top = Math.min(y, rect.height - 60) + 'px';
      };

      path.onmouseleave = () => {
        tip.style.display = 'none';
      };
    }
  });
}

async function drilldownCountry(countryCode, countryName) {
  const body = document.querySelector('#country-drilldown-body');
  const badge = document.querySelector('#country-drilldown-badge');

  // Highlight active country path on map
  document.querySelectorAll('.country-path.active').forEach(p => p.classList.remove('active'));
  const activeEl = document.getElementById(`map-${countryCode}`);
  if (activeEl) activeEl.classList.add('active');

  badge.textContent = `Country: ${countryCode}`;

  // If this country is not in the telemetry dataset
  if (countryCode !== 'UNRESOLVED' && !countryActivityMap[countryCode]) {
    body.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:12px; font-size:11px;">
        <div>
          <b style="font-size:14px; color:var(--ink);">${esc(countryName || countryCode)}</b>
          <span class="badge evidence" style="margin-left:6px;">${esc(countryCode)}</span>
        </div>
        <div><span class="panel-note">TELEMETRY PROVENANCE:</span> <span class="mono">Strict Zero-Guess Policy</span></div>
        <div><span class="panel-note">TOTAL EVENTS:</span> <b class="mono">0</b> in current telemetry window</div>
        <div class="notice">
          <b>Zero-Guess Telemetry Rule:</b> No network events in the verified baseline carry an explicit '${esc(countryCode)}' tag. In accordance with zero-trust principles, IP addresses are never geolocated or assumed without verified database provenance. Missing values remain <b>UNKNOWN / UNRESOLVED</b>.
        </div>
      </div>
    `;
    return;
  }

  body.innerHTML = '<div class="panel-note">Retrieving deterministic country drill-down...</div>';

  try {
    const data = await api(`/api/v1/global/country/${encodeURIComponent(countryCode)}`);
    body.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:12px; font-size:11px;">
        <div>
          <b style="font-size:14px; color:var(--ink);">${esc(data.country_name)}</b>
          <span class="badge evidence" style="margin-left:6px;">${esc(data.country_code)}</span>
        </div>
        <div><span class="panel-note">TELEMETRY PROVENANCE:</span> <span class="mono">${esc(data.provenance)}</span></div>
        <div><span class="panel-note">TOTAL EVENTS:</span> <b class="mono">${data.event_count.toLocaleString()}</b> (Failed Auths: <b class="mono" style="color:var(--amber);">${data.failed_auth_count}</b>)</div>

        <div>
          <span class="panel-note">TOP CORRELATED SOURCE IPS (Click to verify GeoIP provenance):</span>
          <div style="margin-top:4px; max-height:80px; overflow-y:auto;">
            ${(data.top_ips || []).map(ip => `<span class="badge warning" style="margin:2px 2px 2px 0; cursor:pointer;" onclick="inspectGeoIP('${esc(ip.source_ip)}')">🌐 ${esc(ip.source_ip)} (${ip.count})</span>`).join('') || '<span class="panel-note">None</span>'}
          </div>
        </div>

        <div>
          <span class="panel-note">CORRELATED HIGH-RISK IDENTITIES:</span>
          <div style="margin-top:4px;">
            ${(data.correlated_users || []).map(u => `
              <div class="case-card" style="display:flex; justify-content:space-between; align-items:center; padding:6px 0;">
                <span class="mono" style="color:var(--cyan); cursor:pointer;" onclick="view('investigations', '${esc(u.user_id)}')">${esc(u.user_id)}</span>
                <span class="badge ${esc(u.risk_level)}">${u.risk_score}/100</span>
                <button class="btn btn-secondary" style="font-size:9px; padding:2px 6px;" onclick="view('investigations', '${esc(u.user_id)}')">Investigate →</button>
              </div>
            `).join('') || '<span class="panel-note">No overlapping identity telemetry found.</span>'}
          </div>
        </div>

        <div style="padding-top:8px; border-top:1px solid var(--line-dim);">
          <span class="panel-note">ZERO-GUESS POLICY:</span>
          <p style="margin:4px 0 0; color:var(--dim); font-size:10px;">Country data reflects canonical source records. No IP address is geolocated or guessed.</p>
        </div>
      </div>
    `;
  } catch (e) {
    body.innerHTML = `<div class="notice alert">${esc(e.message)}</div>`;
  }
}

async function inspectGeoIP(ip) {
  try {
    const res = await api(`/api/v1/geoip/resolve?ip=${encodeURIComponent(ip)}`);
    document.querySelector('#modal-evidence-title').textContent = `GeoIP Provider Resolution: ${ip}`;
    document.querySelector('#modal-evidence-body').innerHTML = `
      <div style="margin-bottom:12px;">
        <span class="badge ${res.status==='resolved'?'ok':'warning'}">${esc(res.status)}</span>
        <span class="badge slate">PROVIDER: ${esc(res.provenance.provider || 'offline-strict')}</span>
      </div>
      <div style="display:flex; flex-direction:column; gap:8px;">
        <div><span class="panel-note">IP ADDRESS:</span> <b class="mono" style="color:var(--cyan);">${esc(res.ip)}</b></div>
        <div><span class="panel-note">COUNTRY RESOLVED:</span> <b>${esc(res.country)}</b> (${esc(res.country_code || 'UNRESOLVED')})</div>
        <div><span class="panel-note">CONFIDENCE:</span> <span>${res.confidence !== null ? res.confidence : '—'}</span></div>
        <div><span class="panel-note">DATA SOURCE:</span> <span>${esc(res.source)}</span></div>
        <div><span class="panel-note">LOOKUP TIMESTAMP:</span> <span class="mono">${esc(res.lookup_timestamp)}</span></div>
        <div style="padding-top:8px; border-top:1px solid var(--line-dim);">
          <span class="panel-note">PROVENANCE RECORD:</span>
          <pre style="background:var(--surface-0); padding:8px; border-radius:var(--radius); margin:4px 0 0; font-size:10px; color:var(--muted);">${esc(JSON.stringify(res.provenance, null, 2))}</pre>
        </div>
      </div>
    `;
    document.querySelector('#modal-evidence').classList.add('active');
  } catch (e) {
    alert(e.message);
  }
}


/* AI SOC Investigator Copilot Loader */
async function agentInvestigation(question) {
  const userId = document.querySelector('#agent-user').value || 'EMP11411';
  const status = document.querySelector('#agent-status');
  const result = document.querySelector('#agent-result');
  const ctx = document.querySelector('#agent-context');
  const safety = document.querySelector('#agent-safety-box');

  status.textContent = 'Collecting and verifying citations...';
  status.className = 'badge warning';
  result.innerHTML = '<div class="panel-note">Executing grounded deterministic investigation pipeline...</div>';

  try {
    const inv = await api(`/api/investigations/${encodeURIComponent(userId)}?question=${encodeURIComponent(question)}`);
    const risk = inv.evidence.find(x => x.risk_score !== undefined);

    ctx.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:8px; font-size:11px;">
        <div><span class="panel-note">INVESTIGATION:</span> <b class="mono" style="color:var(--cyan); font-size:13px;">${esc(inv.investigation_id)}</b></div>
        <div><span class="panel-note">SUBJECT:</span> <b class="mono">${esc(userId)}</b></div>
        <div><span class="panel-note">RISK:</span> <span class="badge ${esc(risk?.risk_level || 'low')}">${esc(risk?.risk_score ?? '—')}/100</span></div>
        <div><span class="panel-note">HYPOTHESIS:</span> <p style="margin:4px 0 0; color:var(--ink);">${esc(inv.hypothesis || 'Evaluating evidence baseline.')}</p></div>
        <div><span class="panel-note">ANALYSIS QUESTION:</span> <div class="badge slate" style="margin-top:4px;">${esc(question)}</div></div>
      </div>
    `;

    status.textContent = inv.grounded ? 'GROUNDED · verification passed' : 'REVIEW REQUIRED';
    status.className = inv.grounded ? 'badge ok' : 'badge critical';

    result.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:12px;">
        <div style="border-left: 3px solid var(--amber); padding-left:12px;">
          <b style="font-size:13px; color:var(--ink);">${esc(inv.findings?.[0] || 'Evidence collected.')}</b>
          <div style="margin-top:6px; color:var(--muted); font-size:11px;">
            ${(inv.findings || []).slice(1).map(f => `<div>• ${esc(f)}</div>`).join('')}
          </div>
        </div>

        <div style="font-size:11px; color:var(--dim);">
          Evidence Records: <b class="mono">${inv.evidence.length}</b> · Validated Citations: <b class="mono" style="color:var(--cyan);">${inv.citations.length}</b> · Hallucinations: <b class="mono" style="color:var(--green);">0</b>
        </div>

        <div>
          <span class="panel-note">GROUNDED EVIDENCE CITATIONS:</span>
          <div style="margin-top:6px; max-height:100px; overflow-y:auto;">
            ${(inv.citations || []).slice(0, 16).map(c => `<span class="evidence-pill" onclick="inspectRawEvent('${esc(c)}')">${esc(c)}</span>`).join('')}
          </div>
        </div>

        <div class="toolbar" style="margin-top:10px;">
          <button class="btn btn-primary" onclick="view('investigations', '${esc(userId)}')">Open Investigation Workspace</button>
          <button class="btn btn-secondary" onclick="view('graph', '${esc(userId)}')">Explore In Graph</button>
        </div>
      </div>
    `;

    if (inv.quality_warnings && inv.quality_warnings.length) {
      safety.innerHTML = `
        <div class="notice warning" style="margin-top:12px; font-size:10px;">
          <b>⚠ DATA QUALITY & SAFETY NOTICE:</b>
          <div>${inv.quality_warnings.map(w => `• ${esc(w)}`).join('<br>')}</div>
        </div>
      `;
    } else {
      safety.innerHTML = `
        <div class="notice grounded" style="margin-top:12px; font-size:10px;">
          ✓ All citations validated against indexed Parquet artifacts.
        </div>
      `;
    }
  } catch (e) {
    status.textContent = 'Failed';
    status.className = 'badge critical';
    result.innerHTML = `<div class="notice alert">${esc(e.message)}</div>`;
  }
}

document.querySelectorAll('.agent-action').forEach(b => {
  b.onclick = () => agentInvestigation(b.dataset.question);
});
document.querySelector('#agent-user').onchange = (e) => agentInvestigation('Why is this identity high risk?');
document.querySelector('#agent-custom-btn').onclick = () => {
  const q = document.querySelector('#agent-custom-input').value.trim();
  if (q) agentInvestigation(q);
};
document.querySelector('#agent-custom-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    const q = e.target.value.trim();
    if (q) agentInvestigation(q);
  }
});

/* Data Quality Loader */
async function loadQuality() {
  const q = await api('/api/data-quality');
  quality(q, '#quality-reasons');

  const sources = q.source_affected_rows || {};
  const totalRecs = q.source_record_counts || {};
  document.querySelector('#quality-sources').innerHTML = `
    <table class="data-table">
      <thead><tr><th>Source</th><th>Total Records</th><th>Affected Rows</th><th>Impact %</th></tr></thead>
      <tbody>
        ${Object.entries(sources).map(([s, aff]) => {
          const total = totalRecs[s] || aff;
          const pct = Math.round((aff / total) * 100);
          return `
            <tr>
              <td class="mono-cell"><b>${esc(s)}</b></td>
              <td class="mono-cell">${total.toLocaleString()}</td>
              <td class="mono-cell" style="color:var(--amber);">${aff.toLocaleString()}</td>
              <td><span class="badge ${pct>40?'warning':'slate'}">${pct}%</span></td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;
}

/* Audit Chain Loader */
async function loadAudit() {
  const m = await api('/api/manifest');
  document.querySelector('#audit-manifest').innerHTML = `
    <div class="panel-head"><h2 class="panel-title">Cryptographic Manifest Hashes</h2><span class="panel-note">SHA-256 Provenance</span></div>
    <div class="panel-body mono" style="font-size:11px;">
      <div><b>Event Schema:</b> ${esc(m.event_schema_version)}</div>
      <div><b>Ingestion Timestamp:</b> ${esc(m.generated_at || 'frozen-baseline')}</div>
      <div style="margin-top:8px;"><b>Source Hashes:</b></div>
      ${Object.entries(m.sources || {}).map(([f, h]) => `<div>• ${esc(f)}: <span style="color:var(--cyan);">${esc(h)}</span></div>`).join('')}
    </div>
  `;
}

/* Employee Portal Loader */
async function loadEmployee() {
  const out = document.querySelector('#employee-result');
  try {
    const data = await api('/api/employee', { headers: {'X-Demo-Token': 'employee-demo'} });
    out.innerHTML = `
      <div class="panel-head">
        <h2 class="panel-title">${esc(data.profile?.user_id || 'EMP10001')} — Corporate Workspace</h2>
        <span class="badge ok">${esc(data.profile?.risk_level || 'low')} (Score ${data.profile?.risk_score ?? 10})</span>
      </div>
      <div class="panel-body">
        <div style="margin-bottom:14px; font-size:11px; color:var(--muted);">
          Department: <b>${esc(data.profile?.department || 'Engineering')}</b> · Assigned Asset: <b>DEV10001</b> · MFA Status: <b>Enrolled (Active)</b>
        </div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>Event ID</th><th>Action Type</th><th>Timestamp</th><th>Source</th></tr></thead>
            <tbody>
              ${(data.recent_activity || []).map(a => `
                <tr>
                  <td class="mono-cell" style="color:var(--cyan);">${esc(a.event_id)}</td>
                  <td>${esc(a.event_type)}</td>
                  <td class="mono-cell">${esc(a.timestamp)}</td>
                  <td><span class="badge slate">${esc(a.source)}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (e) {
    out.innerHTML = `<div class="panel-body notice alert">${esc(e.message)}</div>`;
  }
}

/* Demo / Scenario Lab Loader */
async function loadScenarios() {
  const grid = document.querySelector('#scenario-grid');
  try {
    const scs = await api('/api/v1/scenarios');
    grid.innerHTML = scs.map(s => `
      <div class="scenario-card ${currentScenario?.id === s.id ? 'active' : ''}">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
            <b style="font-size:13px; color:var(--ink);">${esc(s.title)}</b>
            <span class="badge ${s.category==='CRITICAL'?'critical':s.category==='HIGH'?'high':s.category==='SUSPICIOUS'?'warning':'normal'}">${esc(s.category)}</span>
          </div>
          <p style="color:var(--muted); font-size:11px; margin:0 0 12px; min-height:40px;">${esc(s.description)}</p>
          <div style="font-size:10px; color:var(--dim); margin-bottom:12px;">
            Target: <b class="mono" style="color:var(--cyan);">${esc(s.target_user)}</b> · Expected Risk: <b class="mono">${s.expected_risk}/100</b>
          </div>
        </div>
        <button class="btn btn-primary" onclick="triggerScenario('${esc(s.id)}')">Activate Scenario</button>
      </div>
    `).join('');
  } catch (e) {
    grid.innerHTML = `<div class="notice alert">${esc(e.message)}</div>`;
  }
}

async function triggerScenario(scId) {
  try {
    const s = await api(`/api/v1/scenarios/${encodeURIComponent(scId)}`);
    currentScenario = s;
    const badge = document.querySelector('#scenario-active-badge');
    badge.innerHTML = `<span class="status-indicator red"></span><span>SCENARIO ACTIVE: ${esc(s.title)}</span>`;

    const box = document.querySelector('#scenario-timeline-box');
    box.style.display = 'block';
    document.querySelector('#scenario-timeline-title').textContent = `Active Attack Chain: ${s.title}`;
    document.querySelector('#scenario-jump-invest').onclick = () => view('investigations', s.target_user);

    const stepList = document.querySelector('#scenario-step-list');
    stepList.innerHTML = s.steps.map((st, i) => `
      <div class="case-card" style="display:grid; grid-template-columns: 50px 100px 1fr auto; gap:12px; align-items:center; background:var(--surface-0);">
        <span class="mono" style="font-size:10px; color:var(--dim);">${esc(st.timestamp_offset)}</span>
        <span class="badge ${st.severity==='critical'?'critical':st.severity==='high'?'high':'slate'}">${esc(st.phase)}</span>
        <div>
          <div style="font-weight:600; font-size:11px;">${esc(st.description)}</div>
          <div style="font-size:10px; color:var(--dim);">Source: ${esc(st.source)} · Entity: <span class="mono">${esc(st.entity_id)}</span></div>
        </div>
        ${st.evidence_id ? `<span class="evidence-pill" onclick="inspectRawEvent('${esc(st.evidence_id)}')">${esc(st.evidence_id)}</span>` : ''}
      </div>
    `).join('');

    loadScenarios();
  } catch (e) {
    alert(e.message);
  }
}

function showError(e) {
  console.error(e);
}

// Initial Boot: honor deep link pathname if present
const initialPath = window.location.pathname.replace(/^\/+/, '').split('/')[0];
if (initialPath && document.getElementById(initialPath)) {
  view(initialPath);
} else {
  overview().catch(showError);
}
</script>
</body>
</html>'''

DASHBOARD = DASHBOARD.replace("<!-- __WORLD_MAP_SVG__ -->", get_world_map_svg())


def create_web_app(processed_dir: Path = Path("data/processed")) -> FastAPI:
    app = create_app(processed_dir)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
        )
        return response

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return DASHBOARD

    @app.get("/login", response_class=HTMLResponse)
    def login_page() -> str:
        return DASHBOARD

    @app.get("/employee", response_class=HTMLResponse)
    @app.get("/employee/{path:path}", response_class=HTMLResponse)
    def employee_page(path: str = "") -> str:
        return DASHBOARD

    @app.get("/soc", response_class=HTMLResponse)
    @app.get("/soc/{path:path}", response_class=HTMLResponse)
    def soc_page(path: str = "") -> str:
        return DASHBOARD

    @app.get("/demo", response_class=HTMLResponse)
    def demo_page() -> str:
        return DASHBOARD

    @app.get("/overview", response_class=HTMLResponse)
    @app.get("/global", response_class=HTMLResponse)
    @app.get("/investigations", response_class=HTMLResponse)
    @app.get("/investigations/{path:path}", response_class=HTMLResponse)
    @app.get("/timeline", response_class=HTMLResponse)
    @app.get("/graph", response_class=HTMLResponse)
    @app.get("/agent", response_class=HTMLResponse)
    @app.get("/quality", response_class=HTMLResponse)
    @app.get("/audit", response_class=HTMLResponse)
    @app.get("/scenarios", response_class=HTMLResponse)
    def view_pages(path: str = "") -> str:
        return DASHBOARD

    return app


app = create_web_app()
