# Statement

Replacing one occurrence can be decomposed as deleting that occurrence and then
adding the replacement occurrence. For bounded loss, the corresponding uniform
replace-one indicator is bounded by the delete-one indicator plus the add-one
indicator.

# Definitions used

- ordered sample
- delete-one perturbation
- add-one perturbation
- replace-one perturbation
- bounded 0-1 loss
- worst-case uniform indicator

# Proof sketch

Fix a sample `S`, replacement index `i`, replacement occurrence `z`, and
evaluation pair `(x, y)`. Let `S^{-i}` be the deleted sample and let
`S^{i<-z}` be the replaced sample.

Write

`|loss(h_S, (x,y)) - loss(h_{S^{i<-z}}, (x,y))|`

as

`|loss(h_S, (x,y)) - loss(h_{S^{-i}}, (x,y)) + loss(h_{S^{-i}}, (x,y)) - loss(h_{S^{i<-z}}, (x,y))|`.

Then apply the triangle inequality. The second term is interpreted as an add-one
term because `S^{i<-z}` is obtained by adding `z` to the deleted sample in the
same ordered position convention used by the paper. After taking the supremum
over all legal choices, the uniform inequality follows.

# Full proof or gap

Gap to check carefully:

- whether the add-one notion is defined as append-at-end or as insertion into a
  designated ordered slot;
- whether the theorem is stated for a learner indexed by sample length, so that
  the post-deletion and post-addition hypotheses are well-typed.

The current implementation can support an append-at-end convention, but the
paper statement must match the exact sample-order formalism.

# Counterexample checks

- pointwise LOO does not follow from this inequality;
- the inequality is about uniform worst-case control, not fixed-sample local
  witness behavior.

# Risk

Low mathematical risk, medium notation risk.

# Paper placement

Main text: `04_uniform_calculus`
Appendix: `A_proofs`
