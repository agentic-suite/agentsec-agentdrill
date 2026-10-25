"""``agentdrill verify`` — offline, zero-install bundle/release verification.

Wired to the M18 engine (``lifecycle/verifier.py``): loads a bundle from a
JSON file, verifies it offline (signatures, hashes, manifest, labels,
statistical shape) and prints the three verdicts — **intact / complete /
honest-shaped** — naming the first broken link on failure.

The bundle's ``manifest.key`` field carries the hex-encoded verification key
(the ``key_id`` is in ``manifest.key_id``, default ``local``) so a bundle
verifies offline with zero configuration.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from agentdrill.cli.exit_codes import ExitCode


@click.command()
@click.argument("artifact", required=False)
@click.option("--json", "as_json", is_flag=True, help="Emit the verdict as JSON.")
def verify(artifact: str | None, as_json: bool) -> None:
    """Verify a bundle or release offline: intact, complete, honest-shaped."""
    if artifact is None:
        raise click.UsageError(
            "verify requires a bundle path: agentdrill verify ./bundle.json"
        )

    from agentdrill.lifecycle.verifier import Bundle, verify_bundle
    from agentdrill.registry.signing import HmacSigner

    path = Path(artifact)
    if not path.exists():
        raise click.UsageError(f"bundle not found: {artifact}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise click.UsageError(f"cannot read bundle {artifact}: {exc}") from exc

    try:
        bundle = Bundle.model_validate(data)
    except Exception as exc:  # pydantic ValidationError and friends
        raise click.UsageError(f"invalid bundle {artifact}: {exc}") from exc

    # Offline verification: the bundle carries its own verification key
    # material in the manifest (hex-encoded), matching how agentdrill
    # produces bundles. Without a key in the manifest, the default local
    # key is used — signatures simply fail to verify (fail-closed).
    key_hex = (bundle.manifest or {}).get("key")
    key_id = (bundle.manifest or {}).get("key_id", "local")
    if isinstance(key_hex, str) and key_hex:
        key = bytes.fromhex(key_hex)
    else:
        key = b"agentdrill-local"
    verifier = HmacSigner(key=key, key_id=str(key_id))

    verdict = verify_bundle(bundle, verifier=verifier)

    if as_json:
        click.echo(json.dumps(verdict.model_dump(), indent=2))
    else:
        click.echo(f"intact:       {'PASS' if verdict.intact else 'FAIL'}")
        click.echo(f"complete:      {'PASS' if verdict.complete else 'FAIL'}")
        click.echo(f"honest-shaped: {'PASS' if verdict.honest_shaped else 'FAIL'}")
        if verdict.reasons:
            click.echo("reasons:")
            for reason in verdict.reasons:
                click.echo(f"  - {reason}")

    raise SystemExit(ExitCode.OK if verdict.ok else ExitCode.ORACLE_ERROR)
