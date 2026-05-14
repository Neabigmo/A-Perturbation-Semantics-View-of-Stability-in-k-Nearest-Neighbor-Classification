# Related-Work Table Skeleton

Status: scaffold only. Codex must supply, screen, and judge all literature
entries before this table is used for novelty assessment or paper prose.

## Scope Rules

- Do not treat any row as evidence that a paper is relevant until Codex has
  reviewed it.
- Do not mark novelty risk, theorem overlap, or must-cite status without Codex
  review.
- Keep delete-one, replace-one, add-one, LOO, pointwise, expected, and uniform
  stability notions separate.
- Mark missing fields as `TODO`.

## Table

| Entry ID | Citation Key | Full Citation | Venue/Year | Topic Bucket | Learning Rule | Stability Notion(s) | k-NN Relation | Delete-One Relation | Replace-One Relation | LOO Relation | Main Result Type | Project Relevance | Novelty Risk | Must Cite | Codex Review Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TODO-BE | TODO | TODO | TODO | Bousquet-Elisseeff stability | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | not reviewed | Placeholder bucket from `05_LITERATURE_REVIEW_PROTOCOL.md`. |
| TODO-RW-DW | TODO | TODO | TODO | Rogers-Wagner / Devroye-Wagner deleted estimates and local rules | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | not reviewed | Placeholder bucket from `05_LITERATURE_REVIEW_PROTOCOL.md`. |
| TODO-KR | TODO | TODO | TODO | Kearns-Ron algorithmic stability and LOO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | not reviewed | Placeholder bucket from `05_LITERATURE_REVIEW_PROTOCOL.md`. |
| TODO-CH-STONE | TODO | TODO | TODO | Cover-Hart / Stone k-NN consistency | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | not reviewed | Placeholder bucket from `05_LITERATURE_REVIEW_PROTOCOL.md`. |
| TODO-MNPR | TODO | TODO | TODO | Mukherjee-Niyogi-Poggio-Rifkin LOO stability and consistency | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | not reviewed | Placeholder bucket from `05_LITERATURE_REVIEW_PROTOCOL.md`. |
| TODO-KNN-LOOCV | TODO | TODO | TODO | k-NN LOOCV work | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | not reviewed | Placeholder bucket from `05_LITERATURE_REVIEW_PROTOCOL.md`. |
| TODO-CONFORMAL | TODO | TODO | TODO | Conformal prediction with LOO or replace-one stability | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | not reviewed | Placeholder bucket from `05_LITERATURE_REVIEW_PROTOCOL.md`. |

## Entry Template

```markdown
| ENTRY-ID | citation-key | Full citation text | Venue/Year | Topic bucket | Learning rule | Stability notion(s) | k-NN relation | Delete-one relation | Replace-one relation | LOO relation | Main result type | Project relevance | Novelty risk | Must cite | Codex review status | Notes |
```

## Accepted Status Values

- `not reviewed`
- `screened by Codex`
- `included by Codex`
- `excluded by Codex`

## Formatting Notes

- Use one row per paper or source once Codex supplies the entry.
- Put exact BibTeX keys in `Citation Key` after `paper/refs.bib` is updated.
- Use `TODO` rather than guessing unknown fields.
- Keep `Novelty Risk` as `TODO` until Codex explicitly assigns it.
