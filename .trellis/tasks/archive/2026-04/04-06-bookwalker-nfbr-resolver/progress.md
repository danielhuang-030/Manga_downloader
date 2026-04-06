# Progress — 04-06-bookwalker-nfbr-resolver

## Problem

Runtime errors such as: no `NFBR.a6G.Initializer.*` key with `menu`, or no `moveToPage` after shallow / wrong-type DFS — caused by minified Initializer keys and non-enumerable or function-carried state.

## Solution summary

Multi-strategy resolver `__nfbrResolveMoveHolder()`:

1. Classic `menu` / `views_.menu` → `options.a6l`, direct `moveToPage` or `__nfbrScanA6lForPageMethod`.
2. DFS any `options.a6l` under `Initializer`.
3. Deep graph search including `typeof === 'function'` nodes, `Reflect.ownKeys`, fallbacks on `NFBR.a6G` / `NFBR`.

## Status

Implemented in working tree; commit with README / Trellis docs when ready.
