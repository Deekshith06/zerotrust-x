# Agent architecture

The investigation state is explicit and mutable: intake → evidence collection → correlation → report/grounding validation. The deterministic fallback is the reference behavior. `compile_langgraph()` is optional and only compiles a minimal adapter when LangGraph is installed.

All future model nodes must consume typed state and bounded tool results. Tools must be read-only and parameterized by authorized tenant/resource context. A critic/verification stage must reject unsupported citations, stale evidence, unsupported causal claims, tenant violations, and claims of malicious intent from synthetic telemetry.

The agent summarizes evidence. It does not normalize data, detect threats, assign risk, execute shell/SQL/filesystem/network actions, or perform destructive response.