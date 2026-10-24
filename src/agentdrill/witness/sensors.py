"""Credential + process witnesses (M23 23.3, F87).

Honey credentials / canary tokens (their use is observed by the verifier) and a
process/syscall witness, so credential use and exec are detected. Design:
``docs/prd/26-independent-effect-witness.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HoneyCredential(BaseModel):
    """A honey credential / canary token whose use is watched."""

    name: str
    token: str
    used: bool = False

    def observe_use(self) -> None:
        """Mark the credential as used (the effect was seen)."""
        self.used = True


class ProcessWitness(BaseModel):
    """A process/syscall witness that records observed execs."""

    execs: list[str] = Field(default_factory=list)

    def observe_exec(self, cmd: str, *, benign: bool = False) -> None:
        """Record an exec (benign commands are not effects)."""
        if not benign:
            self.execs.append(cmd)

    @property
    def detected(self) -> bool:
        """Whether any effectful exec was observed."""
        return bool(self.execs)
