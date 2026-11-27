# Performance review — 2026-11-27

Reference: user-supplied Meterleaf v0.2.0 archive, identified by package.json. The user identifies it as the latest recovered local version before discontinuation, not a verified final release. The original archive remains unchanged.

Meterleaf uses session-memory account data reuse, AbortController plus request-generation checks, incremental recharge reveal, memoized date formatting, and an offline static shell that excludes customer responses.

Applied here: preserve existing UI nodes when only progress or list length changes. ApexCraft also precomputes immutable search text. No framework migration, API caching, delayed progress saving, or service worker was introduced. These static applications do not make Meterleaf-style account requests, so cancellation and account-cache logic do not apply.

This reduces avoidable DOM replacement; no measured latency or FPS improvement is claimed. Existing source refresh and progress storage behavior are preserved.
