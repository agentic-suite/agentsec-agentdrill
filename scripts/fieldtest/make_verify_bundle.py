#!/usr/bin/env python3
"""Build a signed, offline-verifiable bundle for the field tests (M31).

Writes a **good** bundle (intact / complete / honest-shaped) and a **tampered**
copy (same bundle, one artifact mutated after signing) so ``agentdrill verify``
can be exercised both ways — exit 0 on the good bundle, exit 3 + reasons on the
tampered one.

Usage::

    python3 make_verify_bundle.py --out DIR [--name bundle]

Writes ``DIR/<name>.json`` (good) and ``DIR/<name>-tampered.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
from pathlib import Path

from agentdrill.registry.signing import HmacSigner


def _sha256(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="directory to write the bundles into")
    ap.add_argument("--name", default="bundle")
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    key = secrets.token_bytes(32)
    signer = HmacSigner(key=key, key_id="local")

    artifacts = {
        "result.json": json.dumps({"blocked": 3, "missed": 1, "degraded": 0}),
        "trace.jsonl": json.dumps(
            [{"case": "replit-destructive-command", "outcome": "blocked"}]
        ),
    }
    signatures = {n: signer.sign(c.encode()) for n, c in artifacts.items()}
    manifest = {
        "pack_hash": _sha256("field-test-pack"),
        "host": "field-test",
        "seeds": [1, 2, 3],
        "environment": ["OMLX_BASE_URL"],
        "hashes": {n: _sha256(c) for n, c in artifacts.items()},
        "key": key.hex(),
        "key_id": "local",
    }
    labels = {"target_attestation": "live"}
    outcome = {"blocked": 3, "missed": 1, "degraded": 0}

    good = {
        "artifacts": artifacts,
        "signatures": signatures,
        "manifest": manifest,
        "labels": labels,
        "outcome": outcome,
    }
    (out / f"{args.name}.json").write_text(json.dumps(good, indent=2), encoding="utf-8")

    tampered = json.loads(json.dumps(good))
    tampered["artifacts"]["result.json"] = json.dumps(
        {"blocked": 9, "missed": 1, "degraded": 0}
    )
    (out / f"{args.name}-tampered.json").write_text(
        json.dumps(tampered, indent=2), encoding="utf-8"
    )

    print(f"ok: wrote {out / f'{args.name}.json'} (good) and "
          f"{out / f'{args.name}-tampered.json'} (tampered)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
