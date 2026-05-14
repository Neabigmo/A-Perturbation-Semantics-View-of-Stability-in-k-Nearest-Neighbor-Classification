# Statement

Odd-k candidate gadgets in the current repository suggest a repeated-occurrence
margin-amplification mechanism extending the 1-NN witness, but no theorem has
yet been proved.

# Definitions used

- deterministic odd-k nearest neighbors
- signed top-k margin
- repeated occurrences with conflicting labels
- computational certificate

# Proof sketch

The current search outputs show candidate samples where the majority margin is
barely on the `0` side before replacement and crosses to the `1` side after an
adversarial replacement. The apparent pattern is:

1. replicate stabilizing occurrences enough times to fill the top-k set;
2. keep the LOO evaluation unchanged at the deleted occurrence;
3. allow one adversarial replacement to cross the sign threshold.

# Full proof or gap

The gap is substantial:

- we do not yet have a theorem that the construction works for all odd `k`;
- we do not yet have a sharp impossibility statement for even `k`;
- the current search records only finite candidates.

# Counterexample checks

- even-k behavior may differ because vote ties already map to label `0`;
- repeated occurrences at the same point can create degenerate but legal
  candidates, so the final paper should separate "clean gadget" and "minimal
  legal gadget" if needed.

# Risk

High.

# Paper placement

Main text: `07_k_gadgets`
Appendix: `B_enumeration_protocol`
