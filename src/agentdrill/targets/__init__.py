"""Target adapters that drive the deployed stack and read back decisions (M5).

``Target`` is the base contract; the deployed-stack targets (``agentgate`` /
``agentkeys`` / ``agentseatbelt`` / ``agentkernel`` / ``policyweave-output`` /
``agenthalt``) land in work item 5.2, recon in 5.3, and attestation in 5.4.
"""

from __future__ import annotations

from agentdrill.models.evidence import Evidence
from agentdrill.targets.base import CommandTarget, Decision, Target

__all__ = ["CommandTarget", "Decision", "Evidence", "Target"]
