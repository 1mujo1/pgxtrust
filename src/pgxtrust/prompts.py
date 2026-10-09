"""Render frozen prompt templates for items and parse model replies.

Prompts are experimental artefacts (master instructions section 29): templates live in
`configs/prompts/<name>_v<NNN>.txt`, are never edited in place, and the template SHA-256 is
recorded with every run. A new wording means a new version file.

Parsing is deliberately strict: a reply counts as an answer only if it is a single option letter
(optionally wrapped in brackets/punctuation, or "Answer: X"). Anything else is recorded as
UNPARSEABLE, which is scored as wrong and reported separately (never silently re-asked).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .items import Item

PROMPT_DIR = Path(__file__).resolve().parents[2] / "configs" / "prompts"
LETTERS = "ABCDEFGH"


def load_template(name: str = "forced_choice_v001") -> tuple[str, str]:
    """Return (template text, SHA-256) for a versioned template."""
    text = (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


_SCORE = re.compile(r"^[≥≤<>]?\s*\d+(\.\d+)?$")


def gene_result_text(lookupkey: str) -> str:
    """'{"CYP2C19": "Poor Metabolizer"}' -> 'CYP2C19 Poor Metabolizer'.

    CPIC stores activity-score genes (e.g. CYP2C9, CYP2D6) as bare numbers; those are shown as
    'CYP2C9 activity score 1.5' so the question is unambiguous.
    """
    data = json.loads(lookupkey) if lookupkey else {}
    parts = []
    for gene, value in sorted(data.items()):
        value = str(value)
        parts.append(f"{gene} activity score {value}" if _SCORE.match(value) else f"{gene} {value}")
    return "; ".join(parts) or "not stated"


def render(item: Item, template: str, context: str = "") -> str:
    """Fill the template for one item. `context` is retrieved evidence (RAG arms) or ''."""
    options_block = "\n".join(f"{LETTERS[i]}. {opt}" for i, opt in enumerate(item.options))
    context_block = f"\nEvidence:\n{context.strip()}\n" if context.strip() else ""
    shown_population = item.display_population or item.population
    population = f" (population: {shown_population})" if shown_population else ""
    return template.format(
        context_block=context_block,
        as_of_date=item.as_of_date,
        drug_name=item.drug_name,
        gene_result=gene_result_text(item.display_lookupkey or item.lookupkey),
        population_clause=population,
        options_block=options_block,
    )


_ANSWER = re.compile(r"^\W*(?:answer\s*[:\-]?\s*)?\(?([A-H])\)?\W*$", re.IGNORECASE)


def parse_answer(reply: str, n_options: int) -> int | None:
    """Option index from a strict single-letter reply, or None if unparseable/out of range."""
    match = _ANSWER.match(reply.strip())
    if not match:
        return None
    index = LETTERS.index(match.group(1).upper())
    return index if index < n_options else None
