# Statement

Within the finite search space implemented by the repository scripts, the
two-point 1-NN witness is minimal with respect to graph size for the searched
LOO-vs-replace-one separation criterion.

# Definitions used

- connected simple labeled graph search space
- ordered samples generated in TASK-007/TASK-008/TASK-009
- computational certificate

# Proof sketch

This is not a paper proof in the usual sense. The repository contains a search
script over the declared finite graph/sample space and a certificate-generation
step that records the observed minimal vertex count. The admissible paper claim
is therefore:

Within the searched finite space, the certificate reports no smaller witness.

# Full proof or gap

Gap is intentional: this remains computational evidence only. To upgrade it, we
would need a non-computational argument that rules out all one-vertex
configurations and any omitted search variants.

# Counterexample checks

- search restrictions must be restated exactly;
- if the search space changed across scripts, the certificate language must use
  the narrowest common space.

# Risk

Medium.

# Paper placement

Main text: `06_1nn_separation`
Appendix: `B_enumeration_protocol`
