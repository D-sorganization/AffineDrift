# MATLAB Best Practices Rules for Cursor

This document consolidates style, correctness, and performance optimization guidelines for MATLAB programming.
It acts like Ruff (lint checks) and Black (formatter) combined—Cursor should apply these rules automatically where possible.

---

## 🎯 Core Principles
- **MUST** write clear, maintainable code before optimizing.
- **MUST** profile before optimizing performance.
- **SHOULD** use vectorization, preallocation, and built-ins when possible.
- **AVOID** unsafe constructs (`inv`, `eval`, `global`).
- **Clarity First**: Write simple, readable, maintainable code.
- **Efficiency**: Use vectorization, preallocation, and built-ins to maximize speed.
- **Column-Major Awareness**: MATLAB stores arrays in column-major order; loop accordingly.
- **Correctness**: Avoid unsafe constructs (`inv`, `eval`, `global`). Validate all inputs and outputs.
- **Profiling**: Optimize only after profiling with `profile`, `timeit`, or `gputimeit`.

---

## 💅 Code Formatting & Style
- **MUST** use 4 spaces (no tabs) and keep lines ≤100 chars.
- **MUST** use camelCase for vars/functions, PascalCase for classes/scripts, UPPER_CASE for constants.
- **MUST** one function per file, filename == function name.
- **SHOULD** use descriptive names (`velocity` not `v`).
- **SHOULD** comment *why*, not *what*.
- **AVOID** `clear all`, `clc`, `close all`, or `addpath` in library code.

---

## ✅ Correctness & Reliability
- **MUST** use `A\b`, not `inv(A)`.
- **MUST** compare floats with tolerance, not `==`.
- **MUST** validate all inputs and outputs.
- **MUST** seed RNG in tests (`rng(0,"twister")`).
- **SHOULD** use `numel`, `size`, `isempty` instead of `length`.
- **AVOID** `eval`, `assignin`, `global`, or shadowing built-ins.
- **NEVER** use `inv(A)`; use `A\b`, `chol`, `qr`, or `svd`.

---

## 🚀 Performance Optimization
- **MUST** profile (`profile`, `timeit`, `gputimeit`) before optimizing.
- **MUST** preallocate arrays (zeros/ones/nan/cell/spalloc).
- **MUST** respect column-major memory order in loops.
- **SHOULD** vectorize loops with built-ins where possible.
- **AVOID** growing arrays, row-major loops, or redundant temporaries.

---

## 🧪 Testing & Tooling
- **MUST** write deterministic unit tests (`matlab.unittest`).
- **MUST** assert correctness with tolerances.
- **SHOULD** use fixtures for CI-friendly tests.
- **AVOID** including figures or UI in tests.

---

## 📋 Code Review Checklist
- [ ] Preallocation everywhere arrays grow
- [ ] Loops vectorized where possible
- [ ] Column-major loop order respected
- [ ] No `inv`, `eval`, or globals
- [ ] Built-ins used over custom loops
- [ ] Input validation present
- [ ] Descriptive names and comments
- [ ] Unit tests written
- [ ] Profiling evidence for performance claims

---

## 🔑 Attitude Check
- If it's slow, **prove it** with the profiler before changing code.
- If it's clever, make it clearer—or make it simpler.
- And remember: **never use `inv`**.






