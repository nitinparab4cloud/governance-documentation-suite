"""
export_artifact.py
-------------------
Regenerates the JSON artifact embedded in index.html's `const ARTIFACT = ...`
line: the worked-example spec plus its Python-rendered reference output,
which the static demo's in-browser self-test checks its own JS-rendered
output against.

Usage:
    python3 export_artifact.py > artifact.json
    # then paste artifact.json's content in place of the object literal
    # after `const ARTIFACT = ` in index.html.
"""

import json
import sys

import yaml

from generate import RISK_MATRIX, render_all

SPEC_PATH = "specs/example_toxic_comment_classifier.yaml"


def build_artifact() -> dict:
    with open(SPEC_PATH) as f:
        spec = yaml.safe_load(f)
    spec.setdefault("generated_date", "2026-10-03")
    spec["overall_risk_level"] = RISK_MATRIX[(spec["risk_probability"], spec["risk_severity"])]
    rendered = render_all(spec)
    return {"spec": spec, "reference_rendered": rendered}


if __name__ == "__main__":
    json.dump(build_artifact(), sys.stdout, indent=2, ensure_ascii=False)
