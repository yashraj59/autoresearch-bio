# Papers Consulted

Starter file copied into the run's working directory at launch. Replace this header block with real entries as families are explored.

The literature-discipline rule (`references/core_protocol.md §13` + `evals/process_checklist.md`) requires:

- At least one entry tagged to each architectural family **before that family produces its first Tier 1 keep**.
- Non-empty diff against this starter after the first 10 experiments. A diff equal to zero after 10 experiments triggers `LITERATURE_DISCIPLINE_VIOLATION` and halts the loop pending amendment.

## Entry template

For every paper, record:

```markdown
### <First-author Year — short title>

- **Citation:** <APA or BibTeX-style citation, including DOI or arXiv id>.
- **Source:** <URL>.
- **Concrete technique extracted:** <one or two sentences naming the specific mechanism>.
- **Family it supports:** <e.g. "Family 2: cross-omic attention">.
- **How it maps to existing code:** <module / function / config flag where the mechanism would land>.
- **Experiments where applied:** <EXPNNN, EXPNNN>.
- **Outcome:** <Tier 1 discard / Tier 1 keep / Tier 2 fail / Tier 3 win, and one-line rationale>.
- **Notes:** <caveats, follow-ups, related work to revisit>.
```

## Entries

<!-- The agent appends real entries below this line. Do not delete the heading. -->
