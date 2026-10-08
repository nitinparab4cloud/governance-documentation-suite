# Field Guide: Governance Documentation Suite

This explains every field in the live demo's guided form — what it is, whether it's required, which
of the six generated documents it feeds, and what it actually means for the governance of the
system you're documenting. Examples below are the real values from the form's prefilled worked
example (a content-moderation classifier, `unitary/toxic-bert`) — reset the form to that example
at any time with the **Reset to example** button if you want to see them in context.

The form has seven collapsible sections. This guide follows the same order.

---

## How it works, in short

You fill in roughly 40 fields describing one AI system. Click **Generate documents** and the same
spec is rendered, unchanged, into six separate governance documents: a Model Card, a Risk
Assessment, a Data Governance Statement, a Human Oversight Design, an Incident Response Runbook,
and a Vendor AI Risk Questionnaire. Because all six come from the same source fields, they can
never contradict each other about what the system is, what its risk level is, or who's
accountable for it — which is the actual problem this tool exists to solve (see the README's "Why
this exists").

Two values are computed for you and never asked for directly:

- **Overall risk level** — computed from Risk probability × Risk severity via the 3×3 risk matrix
  shown on the "Risk matrix" tab (e.g. Medium × Medium = Medium; High × High = Critical).
- **Generated date** — defaults to today's date.

A few fields only appear once another field makes them relevant — the form hides and shows them
automatically:

- **Basis / handling** (data section) only appears once you set "Contains personal data?" to Yes.
- **Contract / DPA reference** (vendor section) only appears once you type a vendor name other
  than "Internal."

---

## 1. Model basics → feeds the Model Card

### `system_name` — System name
**Required.** The name of the system being documented. This becomes the title of all six
documents, so it's worth being specific (not just a product name, but which model/version).
**Example:** `Toxic Comment Classifier (toxic-bert)`

### `version` — Version
**Required.** A version label for this spec. If the model or the spec changes, bump this — the
Risk Assessment's "Review cadence" note explicitly ties re-assessment to material changes.
**Example:** `1.0`

### `owner` — Owner
**Required.** The person or team accountable for this system — who signs off on it, and who gets
asked questions about it. Appears on every document as "Developed by."
**Example:** `Nitin Parab (portfolio project — not affiliated with Unitary AI)`

### `description` — Description
**Required.** A short, plain-language summary of what the model does. This is the first thing a
reviewer reads, so it should stand alone without requiring the rest of the document.
**Example:** *"A BERT-based multi-label classifier that scores a piece of text for six categories
of toxicity (toxic, severe_toxic, obscene, threat, insult, identity_hate), intended as a
content-moderation signal for comment sections or chat platforms."*

### `model_type` — Model type
**Required.** The architecture or model family — the technical answer to "what is this,
mechanically."
**Example:** `Fine-tuned BERT-base, multi-label text classification`

### `base_model` — Base model *(optional)*
Only shown in the Model Card if you fill it in. Useful when your system is a fine-tune or wrapper
around a known foundation model, so a reviewer can look up the base model's own documentation.
**Example:** `bert-base-uncased`

### `intended_use` — Intended use
**Required.** The specific use case this system is designed for — not "what it's capable of," but
what it's actually meant to be used for. This is the line a Risk Assessment is scoped against.
**Example:** *"Flagging candidate-toxic comments for human moderator review on a moderate-traffic
community platform. Output is a confidence score per category, not an automatic removal
decision."*

### `out_of_scope_uses` — Out-of-scope uses
**Required.** Uses the system should **not** be put to. This is one of the most load-bearing
fields in the whole document set — it's what lets you later say "that wasn't an approved use" if
the system gets repurposed without re-review.
**Example:** *"Fully automated content removal without human review; use as the sole basis for
account bans; use on languages other than English...; use as a general sentiment classifier."*

---

## 2. Training & evaluation → feeds the Model Card

### `training_data_summary` — Training data summary
**Required.** What the model was trained on — source, scope, and anything a reviewer needs to
judge whether that training data fits the intended use.
**Example:** *"Jigsaw Toxic Comment Classification Challenge dataset (Wikipedia talk-page
comments, publicly released by Jigsaw/Conversation AI via Kaggle), human-labelled across six
toxicity categories."*

### `evaluation_data_summary` — Evaluation data summary
**Required.** What the model was evaluated on, plus any caveats about how representative that
evaluation is of real deployment conditions.
**Example:** *"Held-out split of the same Jigsaw dataset... Re-validate on a sample of your own
platform's comments before relying on these numbers -- the training distribution... will not match
every deployment's actual comment style or period."*

### `performance_metrics` — Performance metrics (list)
**Required, at least one row.** Each row is a `{name, value}` pair — a metric and its reported
value. Add one row per metric you want listed on the Model Card. Use the "+ Add row" button for
additional metrics, the red ✕ to remove one.
**Example rows:**
| Metric name | Value |
|---|---|
| ROC-AUC (toxic) | 0.98 (per published model card; re-validate for your data) |
| ROC-AUC (identity_hate) | 0.97 (per published model card; smallest-support category -- treat with the most caution) |

### `ethical_considerations` — Ethical considerations
**Required.** Known fairness or ethical risks — documented failure modes, not hypothetical ones.
This is what the Risk Assessment's probability/severity ratings should be consistent with.
**Example:** *"Toxicity classifiers trained on this kind of data are documented in the literature
to have disparate false-positive rates on text that mentions identity terms neutrally (e.g. 'I am
a gay man' scoring higher than a comparable neutral sentence)..."*

### `caveats_recommendations` — Caveats & recommendations
**Required.** Given those risks, how the system should actually be used. This is the practical,
"do this, not that" counterpart to the Ethical Considerations field above.
**Example:** *"Use as a human-in-the-loop triage signal only at first deployment... Do not fully
automate removals until a platform-specific fairness audit... has been run against real traffic."*

---

## 3. Risk → feeds the Risk Assessment

### `risk_probability` — Risk probability
**Required — dropdown: Low / Medium / High.** How likely is it that this system causes harm
through normal operation (not a worst-case edge case — routine behavior).
**Example:** `Medium` — *"false positives/negatives are a routine, expected occurrence for any
moderation classifier, not a rare edge case."*

### `risk_severity` — Risk severity
**Required — dropdown: Low / Medium / High.** If harm does occur, how bad is it? This is
independent of how often it happens.
**Example:** `Medium` — *"the current design keeps a human moderator in the loop before any
account-level action is taken -- severity would move to High if this were reconfigured for
automatic removal or bans without review."*

> Probability × Severity is combined into the **overall risk level** automatically (see the Risk
> matrix tab) — this isn't a field you fill in yourself.

### `affected_parties` — Affected parties (list)
**Required, at least one row.** Who is affected by this system — not just end users, but anyone
downstream of its decisions.
**Example rows:** `Platform users whose comments are scored` · `Users targeted by content the
system fails to catch` · `Human moderators relying on the signal`

### `risk_notes` — Risk rationale
**Required.** Why you chose those probability and severity ratings — a reviewer should be able to
read this and agree (or disagree) with your rating, not just take it on faith.
**Example:** *"Probability rated Medium... Severity rated Medium rather than High because..."*

### `mitigations` — Mitigations in place (list)
**Required, at least one row.** Controls that already exist today to reduce the risk — not planned
ones (though you can note planned mitigations as their own row, as the example does).
**Example rows:** `Human moderator reviews every flagged comment before removal` ·
`Confidence threshold for surfacing to moderators, not for auto-action` · `Planned: identity-term
false-positive audit before any expansion in scope`

### `eu_ai_act_tier` — EU AI Act tier *(optional)*
Only shown in the Risk Assessment if filled in. Your assessment of where this system sits relative
to the EU AI Act's risk tiers (e.g. Annex III or not).
**Example:** *"Likely outside Annex III (not squarely one of the 8 listed sectors) -- but re-run
this through the AI Act Risk Navigator if scope expands..."*

### `eu_ai_act_basis` — EU AI Act basis *(optional)*
Pairs with the field above — the reasoning behind that tier call. Only meaningful alongside
`eu_ai_act_tier`.
**Example:** *"Content moderation is not itself an Annex III category as of the current text;
monitor for sector-specific delegated acts."*

---

## 4. Data → feeds the Data Governance Statement

### `data_sources` — Data sources (list)
**Required, at least one row.** Where the training/operating data comes from.
**Example row:** `Jigsaw Toxic Comment Classification Challenge dataset (public, Kaggle-hosted,
Wikipedia talk-page comments)`

### `pii_present` — Contains personal data?
**Required — dropdown: Yes / No.** Whether personal data is present anywhere in the data this
system touches. This single answer controls whether the "Basis / handling" field below is shown
and whether the generated statement says "Yes" or "No."
**Example:** `Yes`

### `pii_handling_notes` — Basis / handling *(shown only if the field above is "Yes")*
What personal data is present, where it came from, and how it's handled — the detail that makes
"Yes" to the question above actually mean something to a reviewer.
**Example:** *"Wikipedia talk-page comments may incidentally contain personal information
volunteered by the original commenters. No additional PII is collected by this classifier
itself..."*

### `data_governance_measures` — Data governance measures (list)
**Required, at least one row.** Concrete controls on how the data is handled, retained, and
re-used.
**Example rows:** `Inference-time text is retained only as long as the platform's own
moderation-queue retention policy requires` · `No re-training on live platform data without a
separate data governance review` · `Model checkpoint version pinned and logged for every
deployment`

### `data_limitations` — Known data limitations
**Required.** Gaps or biases in the data a reviewer should know about before trusting the model's
output in a new context.
**Example:** *"Training data is English-only, sourced from a single platform (Wikipedia) and time
period (~2017) -- performance on a different platform's comment style, slang, or non-English text
is unvalidated."*

---

## 5. Human oversight → feeds the Human Oversight Design

### `oversight_model` — Oversight model
**Required — dropdown: Human-in-the-loop / Human-over-the-loop / Human-out-of-the-loop.** How much
a human is involved before the system's output leads to a real-world action:
- **Human-in-the-loop** — a human approves every individual decision before it takes effect.
- **Human-over-the-loop** — the system acts, but a human monitors continuously and can override.
- **Human-out-of-the-loop** — the system is fully autonomous, reviewed only periodically.

The guidance embedded in the generated document is: the higher the overall risk level, the closer
to human-in-the-loop this should sit.
**Example:** `Human-over-the-loop`

### `oversight_rationale` — Oversight rationale
**Required.** Why that specific oversight model fits this system's risk level — tie it back to the
overall risk level from the Risk section.
**Example:** *"Matched to a Medium overall risk level: moderators are not required to approve
every single score, but they review every comment the model surfaces above the flagging
threshold..."*

### `escalation_path` — Escalation path
**Required.** Concretely, who a flagged case goes to, and on what timeline.
**Example:** *"Flagged comment > moderation queue > human moderator decision. Comments scoring in
the top confidence band for 'threat' are escalated to a senior moderator within 1 hour..."*

### `contestability_mechanism` — Contestability mechanism
**Required.** How someone affected by a decision can actually challenge it. This is the field that
turns "human oversight" from a design principle into something a real person can use.
**Example:** *"A user whose comment was removed can appeal through the platform's standard
content-appeal form; appeals are reviewed by a moderator who did not make the original removal
decision."*

---

## 6. Incident response → feeds the Incident Response Runbook

### `incident_severity_levels` — Incident severity levels (list of objects)
**Required, at least one row.** Each row is `{name, description, response_time}` — a severity
tier, what qualifies for it, and the target time to respond. Add rows for as many tiers as your
system needs.
**Example rows:**
| Name | Description | Response time |
|---|---|---|
| Sev 1 | Systematic over-flagging or under-flagging affecting a large share of a protected group's comments | 4 hours |
| Sev 2 | Isolated but harmful misclassification (e.g. a credible threat missed) | 24 hours |
| Sev 3 | Isolated false positive with no downstream harm (comment queued, later cleared on review) | 5 business days |

### `incident_detection` — Incident detection
**Required.** How incidents actually get noticed — the detection mechanism, not just "we monitor
it."
**Example:** *"Moderator-reported misclassifications logged in the moderation tool; periodic
sampling audit... run quarterly to catch systematic drift the moderator-reporting channel would
miss."*

### `containment_action` — Containment action
**Required.** The first thing that happens once an incident is confirmed — the immediate stop-gap,
before root-cause work starts.
**Example:** `Raise the flagging threshold or disable auto-surfacing for the affected category
pending review.`

### `incident_contacts` — Incident contacts (list)
**Required, at least one row.** Who gets notified when an incident is confirmed.
**Example rows:** `Trust & Safety lead` · `Model owner`

### `post_incident_review_threshold` — Post-incident review threshold
**Required.** The severity level (by number) at or above which a post-incident review is
mandatory. Plain text so it can reference your own severity numbering.
**Example:** `2` *(meaning: every incident at Severity 2 or worse)*

### `post_incident_review_window` — Post-incident review window
**Required.** How long after the incident the review must be completed.
**Example:** `5 business days`

---

## 7. Sourcing / vendor → feeds the Vendor AI Risk Questionnaire

This section exists even for systems you built entirely in-house — the point is that the same
six-document set is ready, unchanged in shape, the day any part of the system is sourced from (or
replaced by) a third party.

### `vendor_name` — Vendor name
**Required.** Use `Internal` if the system isn't vendor-sourced — this exact value is what makes
the form hide the Contract/DPA field below and what the generated questionnaire checks before
including a contract reference.
**Example:** `Internal`

### `vendor_contract_ref` — Contract / DPA reference *(shown only when vendor name isn't "Internal")*
A reference to the actual contract or data processing agreement governing the relationship.
**Example (if vendor-sourced):** `DPA-2026-01`

### `vendor_data_handling` — Vendor data handling
**Required.** What data the vendor processes and where it's stored/processed. For an internal
system, state plainly that no such relationship exists (see example).
**Example:** `N/A -- internally deployed open-weight model; no vendor data-processing relationship
exists for this checkpoint.`

### `vendor_documentation_available` — Vendor documentation available
**Required.** Whether the vendor provides a model card or equivalent documentation.
**Example:** `N/A`

### `vendor_incident_notification_sla` — Vendor incident notification SLA
**Required.** The vendor's committed time to notify you of a security or model-behavior incident.
**Example:** `N/A`

### `vendor_fairness_testing` — Vendor fairness testing
**Required.** Whether the vendor has independently tested for bias/fairness and will share
results.
**Example:** `N/A -- see this project's own planned fairness audit instead.`

### `vendor_offboarding_terms` — Vendor offboarding terms
**Required.** What happens to your data if the contract ends.
**Example:** `N/A`

### `vendor_audit_rights` — Vendor audit rights
**Required.** Whether the contract includes a right to audit the vendor's own governance controls.
**Example:** `N/A -- this section is retained in every generated document set so it's ready the
day any component of this pipeline is sourced from a vendor instead.`

---

## If you get a "missing required field(s)" error

Clicking **Generate documents** with a required field empty won't crash anything — it shows a red
banner naming exactly which field(s) are missing, by the label shown above. Expand the relevant
section, fill those fields in, and click Generate again. List fields (affected parties,
mitigations, metrics, etc.) count as "missing" only if every row in that list is empty — partial
rows are kept, blank ones are ignored.

## Using your own spec instead of the example

If you already have a spec prepared elsewhere as JSON (for instance, built from the field-reference
spreadsheet), open **Advanced: import / export as JSON** at the bottom of the form, paste it in,
and click **Load JSON into form** — every field above gets populated in one step. The same panel's
**Export form as JSON** button does the reverse: it reads whatever the form currently holds and
produces the equivalent JSON, useful for saving a spec you've built in the form for later.
