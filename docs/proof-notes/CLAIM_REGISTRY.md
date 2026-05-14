# Claim Registry

# C1
Short name: Uniform replace-one through delete-plus-add

## Statement
For bounded loss and deterministic learning rules on ordered samples, a
replace-one perturbation can be decomposed into deleting one occurrence and then
adding the replacement occurrence. The corresponding worst-case stability
indicator is therefore bounded by the sum of the delete-one and add-one
indicators.

## Paper label
Theorem or Proposition

## Dependencies
Definitions: ordered sample, delete-one, add-one, replace-one, bounded loss,
uniform indicator
Prior claims: none
Code artifacts: none

## Proof status
Proof sketch

## Risk
Low

## Where it appears
Section: `04_uniform_calculus`
Appendix: `A_proofs`

## Notes
Novelty is likely in framing, not in the inequality by itself.

# C2
Short name: Deterministic top-k margin crossing criterion

## Statement
For deterministic k-NN with lexicographic neighbor ordering and vote ties
favoring label `0`, a prediction change at query `x` occurs exactly when the
signed top-k margin changes sign relative to the threshold at `0`.

## Paper label
Proposition

## Dependencies
Definitions: deterministic k-NN, ordered top-k neighborhood, signed margin
Prior claims: none
Code artifacts: `src/knn_stability/knn.py`

## Proof status
Proof sketch

## Risk
Medium

## Where it appears
Section: `05_knn_perturbation`
Appendix: `A_proofs`

## Notes
Useful central organizing proposition even if mathematically elementary.

# C3
Short name: Two-point 1-NN LOO vs replace-one separation

## Statement
There exists a two-point graph metric and ordered binary sample for which the
fixed-sample maximum LOO indicator is `0` while the fixed-sample maximum
replace-one indicator is `1`.

## Paper label
Proposition or Example

## Dependencies
Definitions: graph metric, 1-NN, LOO, replace-one
Prior claims: C2
Code artifacts: `outputs/witnesses/1nn_separation_witnesses.json`

## Proof status
Proof sketch

## Risk
Low

## Where it appears
Section: `06_1nn_separation`
Appendix: `A_proofs`

## Notes
The explicit witness should be hand-checked in the paper, not delegated to code.

# C4
Short name: Search minimality over graph size

## Statement
Within the enumerated search space used by the repository scripts, no smaller
graph witness was found before the current two-point witness.

## Paper label
Computational Certificate

## Dependencies
Definitions: search space used by TASK-007/TASK-009
Prior claims: C3
Code artifacts: `experiments/search_minimal_1nn.py`,
`experiments/certify_minimality.py`,
`outputs/witnesses/1nn_minimality_certificate.json`

## Proof status
Computational evidence only

## Risk
Medium

## Where it appears
Section: `06_1nn_separation`
Appendix: `B_enumeration_protocol`

## Notes
Must not be upgraded to theorem without a separate non-computational argument.

# C5
Short name: Odd-k repeated-occurrence gadget lifting

## Statement
Repeated occurrences with conflicting labels appear to create odd-k candidate
patterns whose fixed-sample LOO and replace-one indicators separate in the same
direction as the 1-NN witness.

## Paper label
Conjecture or Computational Certificate

## Dependencies
Definitions: odd-k deterministic k-NN, repeated occurrences
Prior claims: C2, C3
Code artifacts: `experiments/search_k_gadgets.py`,
`outputs/witnesses/k_gadget_candidates.json`

## Proof status
Computational evidence only

## Risk
High

## Where it appears
Section: `07_k_gadgets`
Appendix: `B_enumeration_protocol`

## Notes
Keep theorem language out unless Codex later closes the proof gap.

# C6
Short name: Consistency compatibility

## Statement
Finite worst-case perturbation separations for deterministic k-NN do not, by
themselves, contradict classical distributional and asymptotic consistency
results for nearest-neighbor rules.

## Paper label
Discussion Claim

## Dependencies
Definitions: finite worst-case indicator, distributional consistency
Prior claims: none
Code artifacts: none

## Proof status
Discussion only

## Risk
Low

## Where it appears
Section: `08_consistency`
Appendix: none

## Notes
This is a reader-orientation claim, not a new theorem.
