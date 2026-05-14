# Statement

The paper's finite worst-case perturbation witnesses do not contradict
classical asymptotic consistency results for nearest-neighbor rules.

# Definitions used

- finite worst-case perturbation indicator
- distributional risk
- asymptotic consistency
- deterministic tie-breaking

# Proof sketch

This is a conceptual clarification rather than a theorem. The witness sections
fix a finite metric space and adversarially selected ordered sample, then ask
whether a one-sample perturbation can change a deterministic prediction or
loss. Classical consistency results instead average under an i.i.d. sampling
model and study risk in the large-sample limit.

Since the objects, quantifiers, and asymptotic regimes differ, a finite
worst-case separation between perturbation notions does not by itself imply
anything negative about universal consistency.

# Full proof or gap

No proof upgrade needed. The paper should cite Cover-Hart, Stone, and related
consistency literature carefully and state this only as a discussion claim.

# Counterexample checks

- avoid language suggesting that LOO "fails" in a broad practical sense;
- avoid language suggesting that finite witnesses disprove consistency.

# Risk

Low.

# Paper placement

Main text: `08_consistency`
Appendix: none
