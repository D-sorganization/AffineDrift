---
issue: 5566
summary: "fix discrete-time LTV reachability Gramian backward recursion in correction_authority_evaluator"
---

### Fixed

- Fixed discrete-time LTV reachability Gramian backward recursion in `src/affine_control/correction_authority_evaluator.py` to accumulate via backward state-transition operator $W(k, N) = W(k+1, N) + \Phi(N, k+1) B_k B_k^\top \Phi(N, k+1)^\top$ carrying $\Phi(N, k) = \Phi(N, k+1) A_k$.
- Verified LTI invariance to $< 10^{-12}$ against legacy recursion. No committed artifacts or pages required numerical updates as existing contracts use LTI systems.
