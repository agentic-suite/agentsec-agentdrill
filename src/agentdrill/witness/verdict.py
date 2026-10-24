"""Two-oracle verdict (M23 23.5, F87).

Compare the defense's decision with the independent witness, so enforcement is
adjudicated by **observed effects** — disagreement is a first-class finding.
Design: ``docs/prd/26-independent-effect-witness.md``.
"""

from __future__ import annotations

from pydantic import BaseModel

#: The verdict outcomes (the defense outcome plus the two-oracle additions).
TwoOracleOutcome = str


class TwoOracleVerdict(BaseModel):
    """The two-oracle verdict for one case."""

    case_id: str
    defense: str
    witness: str
    verdict: str
    witness_label: str
    finding: str | None = None


def two_oracle_verdict(
    case_id: str,
    *,
    defense: str,
    effect_seen: bool,
    witness_available: bool = True,
) -> TwoOracleVerdict:
    """Adjudicate a case by the defense decision x the witness effect."""
    if not witness_available:
        return TwoOracleVerdict(
            case_id=case_id,
            defense=defense,
            witness="unavailable",
            verdict=defense,
            witness_label="none",
            finding="witness_unavailable",
        )

    witness = "effect_seen" if effect_seen else "effect_absent"
    if defense == "blocked" and effect_seen:
        verdict, finding = "witness_discrepancy", "witness_discrepancy"
    elif defense == "blocked":
        verdict, finding = "blocked", None
    elif effect_seen:
        verdict, finding = "missed", None
    else:
        verdict, finding = "blocked_silently", None
    return TwoOracleVerdict(
        case_id=case_id,
        defense=defense,
        witness=witness,
        verdict=verdict,
        witness_label="live",
        finding=finding,
    )
