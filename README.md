# CrossSector-2 — Governance Documentation Suite

One YAML spec in, six governance documents out: Model Card, Risk Assessment, Data Governance
Statement, Human Oversight Design, Incident Response Runbook, and Vendor AI Risk Questionnaire —
rendered from the same source of truth so they can never disagree about what the system is. Where
Project 2 in this series audits a model's outputs and Project 4 explains one person's result, this
one asks the question a regulator or review board actually asks first: **where's the paperwork?**

**Live demo:** `huggingface.co/spaces/nparab/governance-documentation-suite` — or open
[`index.html`](index.html) directly in a browser; it's a self-contained, tested static demo with no
server and no network calls.

**Part of:** AI Governance Case Files, a six-project series: [EU AI Act Risk Navigator](https://github.com/nitinparab4cloud/ai-act-risk-navigator) · [Algorithmic Fairness Auditor](https://github.com/nitinparab4cloud/fairness-auditor) · [Governance Documentation Suite](https://github.com/nitinparab4cloud/governance-documentation-suite) · [Explainability Auditor](https://github.com/nitinparab4cloud/explainability-auditor) · [Governed RAG Agent](https://github.com/nitinparab4cloud/governed-rag-agent) · [Agentic AI Incident Response](https://github.com/nitinparab4cloud/agentic-incident-response)

**Origin:** Began as an extension of NUS MSI5004 (AI Governance and Ethics) coursework and was built
out independently, beyond the module syllabus.

**Status:** built and tested end to end — the Jinja2 generator, a worked real example, a Gradio app,
and a JS port of the generator for the live browser demo.

---

## Why this exists

A fairness audit (Legal-1) or a risk classification (CrossSector-1) is only as useful as the paper trail
behind it. Regulators, auditors, and internal review boards don't ask "is this model good" in the
abstract — they ask for specific artifacts: a model card, a documented risk rating, a data
governance statement, a named human-oversight design, an incident runbook, a vendor questionnaire.
Writing those by hand for every system a team ships doesn't scale, and hand-written documentation
drifts out of date the moment anyone changes the model. This project treats the documentation
itself as a build artifact: one spec in, six consistent governance documents out, regenerated on
demand rather than maintained by hand.

## How it works

1. **One spec, six documents** (`generate.py`): every fact about a system — its intended use, its
   training data, its risk rating inputs, its oversight model — is recorded once in a YAML file.
   The generator renders that single source of truth through six Jinja2 templates, so the Model
   Card and the Risk Assessment can never disagree about what the system is for.
2. **The risk score is a visible 3×3 matrix, not a black box.** Probability × severity → Low /
   Medium / High / Critical, following the AI Verify Testing Framework 4.3.1 approach. A reviewer
   can check the computed level against the matrix in ten seconds instead of trusting an opaque
   score.
3. **The six documents cross-reference each other.** The Human Oversight Design cites the computed
   risk level directly; the Incident Response Runbook links back to the Risk Assessment; every
   document links to its siblings. Change the spec once and every downstream document and
   cross-reference updates together.
4. **A vendor questionnaire ships even for internally-built systems** (the worked example's `vendor_name: "Internal"`), so the same six-document set is ready, unchanged in shape, the day any
   component is sourced from — or replaced by — a third party.
5. **Worked example included** (`specs/example_toxic_comment_classifier.yaml`): a real, public,
   small model (`unitary/toxic-bert`, part of the publicly released Detoxify project) run through the full
   pipeline, chosen because it's a plausible stand-in for the kind of content-moderation tooling
   that sits behind any comment section or chat product.

## Sources

- Mitchell, M. et al. (2019), ["Model Cards for Model Reporting"](https://arxiv.org/abs/1810.03993) — the Model Card format this generator follows
- [AI Verify Testing Framework](https://aiverifyfoundation.sg/) 4.3.1 — the probability × severity risk-scoring approach
- Regulation (EU) 2024/1689 (the EU AI Act) — referenced in the Risk Assessment's regulatory-context section
- [Singapore Model AI Governance Framework](https://www.pdpc.gov.sg/help-and-resources/2020/01/model-ai-governance-framework) — human-oversight pattern terminology (human-in-the-loop / over-the-loop / out-of-the-loop)

## Running it

```bash
pip install -r requirements.txt
python3 generate.py specs/example_toxic_comment_classifier.yaml   # writes 6 docs to generated/
python3 export_artifact.py > artifact.json                         # regenerates the JSON embedded in index.html
python3 app.py                                                     # launches the interactive Gradio demo locally
pytest                                                              # 4 tests
```

## Deploying to Hugging Face Spaces

Same free-tier situation as the rest of this series: Hugging Face moved Gradio and Docker Spaces
behind a paid plan, so `app.py` (the full Gradio version) needs a paid Space or local use. For the
free route, `index.html` in this folder is a complete, self-contained, already-tested static demo:
the worked example's spec and its Python-rendered reference output are embedded directly as JSON,
and the generation logic is a line-for-line JS port of `generate.py` / `templates/*.md.j2` —
verified against the Python output with an in-browser self-test banner on every page load (38
assertions).

1. Create a new Space → SDK: **Static** → template: **Blank**.
2. Upload `index.html` from this folder (drag-and-drop through the HF web UI works fine — no git
   needed).
3. Done. No build step, no server, nothing installed at runtime.

If you change a template or the spec schema, regenerate the embedded JSON by re-running
`python3 export_artifact.py > artifact.json` and re-embedding its output into `index.html`'s
`const ARTIFACT = …` line.

## Test scenarios

- `test_generate.py` (4 tests) — the risk matrix maps every (probability, severity) pair to a valid
  level; the worked example's risk level computes correctly from its inputs; all six documents
  render non-empty with no unrendered template tags; `write_outputs` writes all six files to disk.
- The static `index.html` mirrors the same properties as an in-browser self-test (38 assertions,
  shown in the banner on page load): every risk-matrix cell, the worked example's full six-document
  output (spot-checked for content, not just non-empty), both branches of the PII-disclosure
  conditional, both branches of the vendor/internal conditional, and required-field validation.

## Limitations — read before relying on this for anything real

- **This generates documentation, not governance.** A Model Card this tool renders is only as
  accurate as the YAML spec someone filled in — it does not verify any claim, run any fairness
  test, or check any number against the actual model. Legal-1 in this series is the audit; this is
  the paper trail.
- The risk matrix is deliberately simple (3×3, two inputs). A real governance program will want a
  richer scoring model for genuinely high-stakes systems — this one is legible by design, not
  exhaustive.
- Every generated document is a starting draft. A real Risk Assessment, Human Oversight Design, or
  Incident Response Runbook needs sign-off from the people who actually own those decisions, not
  just a filled-in template.
- This is a portfolio project, not a compliance tool in production use anywhere.

## Roadmap / what I'd build next

- A YAML spec validator with helpful error messages (today, a malformed spec fails with whatever
  error Jinja2 or the missing-key access happens to raise).
- A second worked example spec to show the generator isn't tuned to one system (e.g. the
  COMPAS-adjacent model from Legal-1, for maximum continuity across this portfolio).
- A diff view: regenerate after a spec change and show exactly which lines, across which of the six
  documents, actually changed.

## License

All rights reserved — see [LICENSE](LICENSE). Public here for evaluation by prospective employers
and collaborators; not licensed for reuse without permission. This repository is public to review
as part of a portfolio demonstrating AI governance and documentation work.
