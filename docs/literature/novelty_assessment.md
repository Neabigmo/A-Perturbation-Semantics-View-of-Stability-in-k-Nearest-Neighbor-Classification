# Novelty Assessment

## Claim 1: Uniform perturbation calculus
Status: `new framing / easy theorem`

Evidence:
The operation-level observation that a replacement can be decomposed into a
deletion followed by an addition is straightforward. The literature already has
rich replace-one stability formalisms and modern uniform-stability bounds, so a
claim of foundational novelty would be unsafe. What does look publishable is a
clean reframing that places delete-one, add-one, replace-one, and LOO in one
deterministic ordered-sample calculus with explicit evaluation-point hygiene.

Relevant literature:
`bousquet2002stability`, `kutin2002almost`, `feldman2019high`,
`bousquet2020sharpening`

Risk:
Medium. The relation itself is probably folklore-level once definitions are
fixed.

Recommended paper label:
Main-text theorem/proposition with modest novelty framing. Emphasize the
calculus and the evaluation-point distinctions, not the inequality alone.

## Claim 2: Exact deterministic k-NN perturbation criterion
Status: `likely new proposition / unclear`

Evidence:
We did not identify a source that states the deterministic ordered top-k margin
crossing criterion in the exact form used here, with duplicate occurrences,
sample-index tie-breaking, and label ties resolved toward `0`. Parts of it are
elementary once the rule is fixed, but the exact statement is still worth
writing because it is the bridge from definitions to witnesses and figures.

Relevant literature:
`cover1967nearest`, `stone1977consistent`, `collins2020consistency`

Risk:
Medium. The statement may be regarded as an explicit unpacking of the
deterministic rule rather than a deep theorem.

Recommended paper label:
`Proposition`, presented as the technical heart that makes later examples
transparent.

## Claim 3: 1-NN finite graph separation between LOO and replace-one
Status: `likely new example / low direct overlap found`

Evidence:
The current search and hand-checkable two-point witness appear to give a clean
finite metric example where fixed-sample LOO remains zero while fixed-sample
replace-one is one. We did not find prior sources presenting this exact
separation with deterministic tie-breaking and explicit finite graph metrics.

Relevant literature:
`rogers1978finite`, `devroye1979distribution`, `kearns1999algorithmic`,
`ndiaye2022stability`, `pournaderi2024training`

Risk:
Medium. The phenomenon might be considered simple after definitions are made
precise, but the explicit witness still looks publishable as an example.

Recommended paper label:
Explicit `Proposition` or `Example` for the hand-checked witness; separate
`Computational Certificate` for search minimality.

## Claim 4: Extension / gadget lifting to general k
Status: `unclear / computational evidence only`

Evidence:
The repository currently has deterministic search outputs for odd `k` candidate
patterns, but no proof note yet upgrades them into a theorem. The current
evidence supports a conjectural repeated-occurrence margin-amplification story,
not a proved lifting theorem.

Relevant literature:
No directly matching prior theorem found in the inspected sources; this absence
is not enough to claim novelty.

Risk:
High.

Recommended paper label:
`Computational Certificate` plus `Conjecture`, unless a full proof is written.

## Claim 5: Consistency compatibility
Status: `known / discussion framing`

Evidence:
Classical nearest-neighbor consistency results concern distributional and
asymptotic behavior, while this project studies finite worst-case perturbation
effects. The compatibility claim is explanatory and should not be sold as a new
consistency theorem.

Relevant literature:
`cover1967nearest`, `cover1968estimation`, `stone1977consistent`,
`mukherjee2006learning`

Risk:
Low if stated only as clarification.

Recommended paper label:
`Discussion Claim`.

## Overall recommendation
Main contribution:
An explicit deterministic perturbation calculus for local learning rules, with
ordered-sample definition hygiene and a memorable finite-metric witness showing
that LOO and adversarial replace-one are not interchangeable.

Secondary contribution:
An exact deterministic k-NN margin-crossing criterion and a reproducible
computational witness/certificate pipeline.

Things not to claim:

- Do not claim a new generalization bound.
- Do not claim the first theory of k-NN stability in any broad sense.
- Do not claim odd-k lifting as theorem without proof.
- Do not claim computational minimality as mathematical minimality.

Things to move to appendix:

- Exhaustive enumeration protocol details.
- Hashes and certificate-generation details.
- Additional gadget candidates and negative-search summaries.
