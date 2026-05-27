# Papers Consulted

Starter file copied into the run's working directory at launch. Replace this header block with real entries as families are explored.

The literature-discipline rule (`references/core_protocol.md §13` + `evals/process_checklist.md`) requires:

- At least one entry tagged to each architectural family **before that family produces its first Tier 1 keep** (`LITERATURE_GROUNDING_MISSING` otherwise).
- Non-empty diff against this starter after the first 10 experiments (`LITERATURE_DISCIPLINE_VIOLATION` otherwise).
- A literature pass is triggered by `LITERATURE_PASS_REQUIRED_BY_STALL` events (three consecutive Tier 1 discards in a family, a Tier 2 failure with protected-metric regression, etc.) — the next mechanism in the stalled family may not launch until this file gains a new entry tagged to that family.

## Canonical Search Surfaces

Pick at least three per pass from the relevant domain. See `references/core_protocol.md §13` for the rule.

**Biology / scientific ML:** arXiv (q-bio, stat.ML, cs.LG), bioRxiv, medRxiv, PubMed / NCBI, OpenAlex, Semantic Scholar, Connected Papers, OpenReview (bio tracks), and domain databases as search surfaces (Reactome, MSigDB, GO, ClinVar, GTEx, ENCODE, HCA, STRING, KEGG, DepMap). If running under Codex with the `$life-science-research` skill, invoke it as the primary surface for bio queries.

**General ML / software / agents / benchmarking:** arXiv (cs.LG / cs.AI / cs.CL / cs.CV / cs.SE / stat.ML), Semantic Scholar, OpenReview, Papers with Code, NeurIPS / ICLR / ICML / ACL / EMNLP / ICSE / FSE proceedings, ACL Anthology. Google Scholar only as a last-resort breadth surface.

## Fetch Fingerprint Declaration

Declare the agent's fetch fingerprint here at run start. This must match the entry in `leakage_preflight.md` and stay consistent across the run (re-declare on amendment).

```yaml
fetch_fingerprint:
  mode: <agent_harness_web_tools | semantic_scholar_api | mcp_paper_search>
  details:
    # For agent_harness_web_tools:
    harness: <Claude Code | Codex | Cursor | Aider | OpenDevin | custom>
    tools_used: [WebSearch, WebFetch]
    # For semantic_scholar_api:
    api_version: <e.g. v1>
    api_key_env_var: SEMANTIC_SCHOLAR_API_KEY
    # For mcp_paper_search:
    mcp_servers: [<server-name@version>, ...]   # e.g. mcp-paper-search@0.3, pubmed-mcp@1.2
```

## Entry Template

For every paper, record:

```markdown
### <First-author Year — short title>

- **Citation:** <APA or BibTeX-style citation, including DOI or arXiv id>.
- **Source URL:** <URL>.
- **Search surface that returned it:** <e.g. "Semantic Scholar query 'cross-omic attention BRCA'", "bioRxiv subject q-bio.QM 2025">.
- **Fetch fingerprint:** <WebFetch in Codex | mcp-paper-search v0.3 | Semantic Scholar API v1>.
- **Concrete technique extracted:** <one or two sentences naming the specific mechanism>.
- **Family it supports:** <e.g. "Family 2: cross-omic attention">.
- **How it maps to existing code:** <module / function / config flag where the mechanism would land>.
- **Identity preservation:** <preserves | violates — and which identity commitment>.
- **Experiments where applied:** <EXPNNN, EXPNNN>.
- **Outcome:** <Tier 1 discard / Tier 1 keep / Tier 2 fail / Tier 3 win, and one-line rationale>.
- **Notes:** <caveats, follow-ups, related work to revisit>.
```

## Entries

<!-- The agent appends real entries below this line. Do not delete the heading. -->
