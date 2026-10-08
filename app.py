"""
app.py
------
Interactive Gradio demo for the Governance Documentation Suite (CrossSector-2).

The deliverable isn't six hand-written documents -- it's a process that turns
one YAML spec into six governance documents (Model Card, Risk Assessment,
Data Governance Statement, Human Oversight Design, Incident Response Runbook,
Vendor AI Risk Questionnaire). This app makes that process interactive: edit
the spec, regenerate, read the output.
"""

import pathlib

import gradio as gr
import yaml

from generate import DOCUMENTS, RISK_MATRIX, load_spec, render_all

EXAMPLE_SPEC_PATH = pathlib.Path(__file__).parent / "specs" / "example_toxic_comment_classifier.yaml"
EXAMPLE_SPEC_TEXT = EXAMPLE_SPEC_PATH.read_text()

DOC_TITLES = {
    "model_card.md": "Model Card",
    "risk_assessment.md": "Risk Assessment",
    "data_governance.md": "Data Governance Statement",
    "human_oversight.md": "Human Oversight Design",
    "incident_response.md": "Incident Response Runbook",
    "vendor_risk_questionnaire.md": "Vendor AI Risk Questionnaire",
}

REQUIRED_FIELDS = [
    "system_name", "version", "owner", "description", "model_type",
    "intended_use", "out_of_scope_uses", "training_data_summary",
    "evaluation_data_summary", "performance_metrics", "ethical_considerations",
    "caveats_recommendations", "risk_probability", "risk_severity",
    "affected_parties", "risk_notes", "mitigations", "data_sources",
    "pii_present", "data_governance_measures", "data_limitations",
    "oversight_model", "oversight_rationale", "escalation_path",
    "contestability_mechanism", "incident_severity_levels",
    "incident_detection", "containment_action", "incident_contacts",
    "post_incident_review_threshold", "post_incident_review_window",
    "vendor_name", "vendor_data_handling", "vendor_documentation_available",
    "vendor_incident_notification_sla", "vendor_fairness_testing",
    "vendor_offboarding_terms", "vendor_audit_rights",
]


def generate_from_yaml(yaml_text: str):
    try:
        raw = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        err = f"**YAML parse error:** {e}"
        return (err,) + tuple("" for _ in DOCUMENTS)

    if not isinstance(raw, dict):
        err = "**Spec error:** the YAML must parse to a mapping of field names to values (see the worked example)."
        return (err,) + tuple("" for _ in DOCUMENTS)

    missing = [f for f in REQUIRED_FIELDS if f not in raw]
    if missing:
        err = "**Spec error — missing required field(s):** " + ", ".join(missing)
        return (err,) + tuple("" for _ in DOCUMENTS)

    try:
        # load_spec() re-reads from a path, so replicate its two side effects
        # (default generated_date, computed overall_risk_level) directly on
        # the already-parsed dict instead of round-tripping through a file.
        import datetime
        spec = dict(raw)
        spec.setdefault("generated_date", datetime.date.today().isoformat())
        spec["overall_risk_level"] = RISK_MATRIX.get(
            (spec.get("risk_probability"), spec.get("risk_severity")), "Unrated"
        )
        rendered = render_all(spec)
    except Exception as e:  # noqa: BLE001 - surface any template/spec mismatch to the user
        err = f"**Generation error:** {e}"
        return (err,) + tuple("" for _ in DOCUMENTS)

    risk_line = (
        f"**Overall risk level: {spec['overall_risk_level']}** "
        f"(probability: {spec.get('risk_probability')} × severity: {spec.get('risk_severity')})"
    )
    return (risk_line,) + tuple(rendered[d] for d in DOCUMENTS)


def risk_matrix_markdown() -> str:
    levels = ["Low", "Medium", "High"]
    header = "| Probability \\ Severity | " + " | ".join(levels) + " |"
    sep = "|---|" + "---|" * len(levels)
    rows = [header, sep]
    for p in levels:
        cells = [RISK_MATRIX[(p, s)] for s in levels]
        rows.append(f"| **{p}** | " + " | ".join(cells) + " |")
    return "\n".join(rows)


METHODOLOGY_MD = """
## Why this exists

A fairness audit (Legal-1) or a risk classification (CrossSector-1) is only as
useful as the paper trail behind it. Regulators, auditors, and internal
review boards don't ask "is this model good" in the abstract — they ask for
specific artifacts: a model card, a documented risk rating, a data
governance statement, a named human-oversight design, an incident runbook,
a vendor questionnaire. Writing those by hand for every system a team ships
doesn't scale, and hand-written documentation drifts out of date the moment
anyone changes the model. This project treats the documentation itself as
a build artifact: one YAML spec in, six consistent governance documents out,
regenerated on demand rather than maintained by hand.

## How it works

1. **One spec, six documents.** Every fact about a system — its intended
   use, its training data, its risk rating inputs, its oversight model — is
   recorded once in a YAML file. `generate.py` renders that single source of
   truth through six Jinja2 templates, so the Model Card and the Risk
   Assessment can never disagree about what the system is for.
2. **The risk score is a visible 3×3 matrix, not a black box.** Probability
   × severity → Low / Medium / High / Critical, following the AI Verify
   Testing Framework 4.3.1 approach. A reviewer can check the computed level
   against the matrix in ten seconds — see the Risk Matrix tab.
3. **The six documents cross-reference each other.** The Human Oversight
   Design cites the computed risk level directly; the Incident Response
   Runbook links back to the Risk Assessment; every document links to its
   siblings. Change the spec once and every downstream document and
   cross-reference updates together.
4. **A vendor questionnaire ships even for internally-built systems**, so
   the same six-document set is ready, unchanged in shape, the day any
   component is sourced from — or replaced by — a third party.

## Sources

- Mitchell, M. et al. (2019), ["Model Cards for Model Reporting"](https://arxiv.org/abs/1810.03993) — the Model Card format this generator follows
- [AI Verify Testing Framework](https://aiverifyfoundation.sg/) 4.3.1 — the probability × severity risk-scoring approach
- Regulation (EU) 2024/1689 (the EU AI Act) — referenced in the Risk Assessment's regulatory-context section
- [Singapore Model AI Governance Framework](https://www.pdpc.gov.sg/help-and-resources/2020/01/model-ai-governance-framework) — human-oversight pattern terminology (human-in-the-loop / over-the-loop / out-of-the-loop)

## Limitations — read before relying on this for anything real

- **This generates documentation, not governance.** A Model Card this tool
  renders is only as accurate as the YAML spec someone filled in — it does
  not verify any claim, run any fairness test, or check any number against
  the actual model. Legal-1 in this series is the audit; this is the
  paper trail.
- The risk matrix is deliberately simple (3×3, two inputs). A real
  governance program will want a richer scoring model for genuinely
  high-stakes systems — this one is legible by design, not exhaustive.
- Every generated document is a starting draft. A real Risk Assessment,
  Human Oversight Design, or Incident Response Runbook needs sign-off from
  the people who actually own those decisions, not just a filled-in
  template.
- This is a portfolio project, not a compliance tool in production use
  anywhere.
"""


with gr.Blocks(title="Governance Documentation Suite") as demo:
    gr.Markdown("# Governance Documentation Suite")
    gr.Markdown(
        "One YAML spec in, six governance documents out: Model Card, Risk Assessment, "
        "Data Governance Statement, Human Oversight Design, Incident Response Runbook, "
        "and Vendor AI Risk Questionnaire — consistent with each other because they're "
        "rendered from the same source of truth."
    )

    with gr.Tab("Generate from a spec"):
        gr.Markdown(
            "Edit the YAML spec below (prefilled with a worked example — the "
            "`unitary/toxic-bert` content-moderation classifier) and regenerate."
        )
        with gr.Row():
            with gr.Column(scale=1):
                spec_box = gr.Code(value=EXAMPLE_SPEC_TEXT, language="yaml", label="Spec (YAML)", lines=30)
                generate_btn = gr.Button("Generate documents", variant="primary")
            with gr.Column(scale=2):
                risk_out = gr.Markdown()
                doc_outputs = {}
                with gr.Tabs():
                    for doc_name in DOCUMENTS:
                        with gr.Tab(DOC_TITLES[doc_name]):
                            doc_outputs[doc_name] = gr.Markdown()

        generate_btn.click(
            fn=generate_from_yaml,
            inputs=[spec_box],
            outputs=[risk_out] + [doc_outputs[d] for d in DOCUMENTS],
        )
        demo.load(
            fn=generate_from_yaml,
            inputs=[spec_box],
            outputs=[risk_out] + [doc_outputs[d] for d in DOCUMENTS],
        )

    with gr.Tab("Risk matrix"):
        gr.Markdown(
            "## How the overall risk level is computed\n\n"
            "Probability of harm × severity if it occurs → one of four levels. "
            "Deliberately simple: a reviewer should be able to sanity-check this "
            "table in ten seconds, which is the point of using a visible matrix "
            "instead of an opaque score.\n\n" + risk_matrix_markdown()
        )

    with gr.Tab("Methodology & Sources"):
        gr.Markdown(METHODOLOGY_MD)


if __name__ == "__main__":
    demo.launch()
